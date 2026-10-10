"""Verified arithmetic cache: every stored predecessor is still checked each read.

This reduces repeated arithmetic, not the need to inspect retained lineage bytes.
"""
from fractions import Fraction
from collections import OrderedDict
import json
import re
from context_continuation import Continuation,digest,operate

MAX_CACHED_CONTINUATIONS=4
MAX_CACHED_RAW_BYTES=1024*1024

FIELDS={'continuation','parent','sequence','context','axis','parameter','input','result'}


class IncrementalContinuation(Continuation):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._verified=OrderedDict()

    def _replay(self,db,identifier,head):
        genesis=db.execute('SELECT genesis_context FROM continuation WHERE id=?',(identifier,)).fetchone()
        if genesis is None or genesis[0] not in self.contexts:raise ValueError('unregistered genesis context')
        policy=digest({'contexts':self.contexts,'transitions':sorted(self.transitions),'genesis':genesis[0]})
        saved=self._verified.get(identifier)
        if saved is None or saved['policy']!=policy:saved={'policy':policy,'events':{},'states':{None:(Fraction(1),0,genesis[0])}}
        chain=[];cursor=head;seen=set();new={}
        while cursor is not None:
            if cursor in seen or len(chain)>=4096:raise ValueError('cyclic or oversized predecessor lineage')
            seen.add(cursor)
            row=db.execute('SELECT body FROM lineage WHERE hash=?',(cursor,)).fetchone()
            if row is None:raise ValueError('broken predecessor lineage')
            previous=saved['events'].get(cursor)
            if previous is not None and row[0]==previous['raw']:
                body=previous['body']
            else:
                body=json.loads(row[0])
                if not isinstance(body,dict) or set(body)!=FIELDS:raise ValueError('lineage frame mismatch')
                if body['parent'] is not None and (type(body['parent']) is not str or re.fullmatch('[0-9a-f]{64}',body['parent']) is None):raise ValueError('invalid predecessor reference')
                if digest(body)!=cursor or body['continuation']!=identifier:raise ValueError('lineage identity/digest mismatch')
            new[cursor]={'raw':row[0],'body':body};chain.append((cursor,body));cursor=body['parent']
        value=Fraction(1);count=0;prior=genesis[0];states={None:(value,count,prior)}
        for key,body in reversed(chain):
            count+=1
            prior_event=saved['events'].get(key)
            cached=saved['states'].get(key)
            if cached is not None and prior_event is not None and new[key]['raw']==prior_event['raw']:
                value,verified_count,prior=cached
                if verified_count!=count:raise ValueError('cached lineage position mismatch')
            else:
                current=self.admitted(body['context'])
                if current!=prior and (prior,current) not in self.transitions:raise ValueError('cross-origin transition is not admitted')
                if type(body['sequence']) is not int or body['sequence']!=count or body['input']!=str(value):raise ValueError('lineage sequence/input mismatch')
                value=operate(value,body['axis'],body['parameter'])
                if max(value.numerator.bit_length(),value.denominator.bit_length())>4096:raise ValueError('arithmetic representation budget exceeded')
                if body['result']!=str(value):raise ValueError('coordinate vector does not match predecessor operation')
                prior=current
            states[key]=(value,count,prior)
        # Publish only after complete verification; cached rows rolled back by caller
        # cannot be reused unless exact bytes are found again in a later snapshot.
        if sum(len(e['raw'].encode()) for e in new.values())<=MAX_CACHED_RAW_BYTES:
            self._verified[identifier]={'policy':policy,'events':new,'states':states}
            self._verified.move_to_end(identifier)
            while len(self._verified)>MAX_CACHED_CONTINUATIONS:self._verified.popitem(last=False)
        else:self._verified.pop(identifier,None)
        return value,count,prior
