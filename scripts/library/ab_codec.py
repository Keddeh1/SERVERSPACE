"""Owner A=one run, B=zero run; canonical framed reversible encoding."""
import re
MAX_BYTES=1024*1024
MAX_DEPTH=8

def pack(raw):
    if not isinstance(raw,bytes) or len(raw)>MAX_BYTES:raise ValueError('binary input exceeds budget')
    runs=[];last=None;count=0
    for byte in raw:
        for shift in range(7,-1,-1):
            label='A' if (byte>>shift)&1 else 'B'
            if label==last:count+=1
            else:
                if last is not None:runs.append(last+str(count))
                last=label;count=1
    if last is not None:runs.append(last+str(count))
    return ('AB1:'+str(len(raw)*8)+':'+''.join(runs)).encode('ascii')

def unpack(frame):
    if not isinstance(frame,bytes) or len(frame)>16*MAX_BYTES+64:raise ValueError('frame exceeds budget')
    try:s=frame.decode('ascii')
    except UnicodeDecodeError as e:raise ValueError('non-ASCII frame') from e
    m=re.fullmatch(r'AB1:(0|[1-9][0-9]{0,7}):(.*)',s)
    if not m:raise ValueError('invalid frame')
    length=int(m[1]);tokens=m[2]
    if length>MAX_BYTES*8 or length%8:raise ValueError('invalid binary length')
    result=bytearray();value=0;used=0;total=0;pos=0;last=None
    for token in re.finditer(r'([AB])([1-9][0-9]{0,7})',tokens):
        if token.start()!=pos or token[1]==last:raise ValueError('noncanonical run')
        label=token[1];count=int(token[2]);total+=count
        if total>length:raise ValueError('run exceeds declared length')
        for _ in range(count):
            value=(value<<1)|(label=='A');used+=1
            if used==8:result.append(value);value=0;used=0
        last=label;pos=token.end()
    if pos!=len(tokens) or total!=length:raise ValueError('truncated or malformed runs')
    return bytes(result)

def cascade(raw,depth):
    if type(depth) is not int or not 1<=depth<=MAX_DEPTH:raise ValueError('invalid cascade depth')
    for _ in range(depth):raw=pack(raw)
    return raw

def restore(frame,depth):
    if type(depth) is not int or not 1<=depth<=MAX_DEPTH:raise ValueError('invalid cascade depth')
    for _ in range(depth):frame=unpack(frame)
    return frame

ONES='CDEFGHIJK'
ZEROS='LMNOPQRST'

def compact_pack(raw):
    # Reuse the qualified owner run semantics; remove redundant A/B markers.
    plain=pack(raw).decode('ascii');_,length,runs=plain.split(':',2);tokens=[]
    for run in re.finditer(r'([AB])([1-9][0-9]*)',runs):
        alphabet=ONES if run[1]=='A' else ZEROS;count=int(run[2]);whole,remainder=divmod(count,9)
        tokens.append(alphabet[-1]*whole)
        if remainder:tokens.append(alphabet[remainder-1])
    return ('ABC1:'+length+':'+''.join(tokens)).encode('ascii')

def compact_unpack(frame):
    if not isinstance(frame,bytes) or len(frame)>MAX_BYTES*8+64:raise ValueError('compact frame exceeds budget')
    try:text=frame.decode('ascii')
    except UnicodeDecodeError as e:raise ValueError('non-ASCII compact frame') from e
    m=re.fullmatch(r'ABC1:(0|[1-9][0-9]{0,7}):([C-T]*)',text)
    if not m:raise ValueError('invalid compact frame')
    length=int(m[1])
    if length>MAX_BYTES*8 or length%8:raise ValueError('invalid compact bit length')
    runs=[];label=None;count=0;previous=0;total=0
    for symbol in m[2]:
        current='A' if symbol in ONES else 'B';alphabet=ONES if current=='A' else ZEROS;n=alphabet.index(symbol)+1
        if current==label:
            if previous!=9:raise ValueError('noncanonical split run')
            count+=n
        else:
            if label is not None:runs.append(label+str(count))
            label=current;count=n
        total+=n
        if total>length:raise ValueError('compact run exceeds length')
        previous=n
    if label is not None:runs.append(label+str(count))
    if total!=length:raise ValueError('compact length mismatch')
    return unpack(('AB1:'+str(length)+':'+''.join(runs)).encode('ascii'))
