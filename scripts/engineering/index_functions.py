#!/usr/bin/env python3
"""Static function breakdown; not a claim that functions were dynamically tested."""
import ast,hashlib,json,argparse
from pathlib import Path
class Functions(ast.NodeVisitor):
    def __init__(self,source,path):self.source=source;self.path=path;self.scope=[];self.rows=[]
    def visit_ClassDef(self,node):
        self.scope.append(node.name);self.generic_visit(node);self.scope.pop()
    def visit_FunctionDef(self,node):
        self.scope.append(node.name)
        text=ast.get_source_segment(self.source,node) or ''
        self.rows.append({'path':self.path,'function':'.'.join(self.scope),'line':node.lineno,'end_line':node.end_lineno,'signature':ast.unparse(node.args),'docstring':ast.get_docstring(node),'calls':sorted({ast.unparse(n.func) for n in ast.walk(node) if isinstance(n,ast.Call)}),'explicit_raises':sorted({ast.unparse(n.exc) for n in ast.walk(node) if isinstance(n,ast.Raise) and n.exc is not None}),'contains_pass_or_notimplemented':any(isinstance(n,ast.Pass) or isinstance(n,ast.Name) and n.id=='NotImplementedError' for n in ast.walk(node)),'sha256':hashlib.sha256(text.encode()).hexdigest(),'qualification':'static source inventory; consult executed test receipts separately'})
        self.generic_visit(node);self.scope.pop()
    visit_AsyncFunctionDef=visit_FunctionDef

def main():
    p=argparse.ArgumentParser();p.add_argument('roots',nargs='+',type=Path);args=p.parse_args();groups=[]
    for root in args.roots:
        rows=[]
        for path in sorted(root.rglob('*.py')):
            if any(x in path.parts for x in ['.venv','__pycache__','.git']):continue
            source=path.read_text();v=Functions(source,str(path.relative_to(root)));v.visit(ast.parse(source));rows.extend(v.rows)
        groups.append({'source_root':str(root),'functions':rows,'count':len(rows)})
    print(json.dumps({'schema':'kex.function-breakdown.v1','groups':groups},indent=2))
if __name__=='__main__':main()
