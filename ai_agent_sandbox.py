import argparse
import json
import shutil
import time
import uuid
from collections import deque
from pathlib import Path
class Sandbox:
    def __init__(self,root,max_ops=25,max_write_bytes=65536,max_file_bytes=65536):
        self.root=Path(root).resolve()
        self.root.mkdir(parents=True,exist_ok=True)
        self.max_ops=max_ops
        self.max_write_bytes=max_write_bytes
        self.max_file_bytes=max_file_bytes
        self.permissions={"read":True,"write":True,"list":True,"delete":False}
        self.ops=0
        self.writes=0
        self.audit=[]
        self.snapshot={}
    def path(self,relative):
        raw=Path(str(relative))
        if raw.is_absolute():raise PermissionError("Absolute paths are not allowed.")
        target=(self.root/raw).resolve()
        if target!=self.root and self.root not in target.parents:raise PermissionError("Path escapes sandbox.")
        return target
    def begin(self):
        self.snapshot={}
        for p in self.root.rglob("*"):
            if p.is_file():self.snapshot[p.relative_to(self.root).as_posix()]=p.read_bytes()
        self.snapshot["__dirs__"]=[p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_dir()]
        self.ops=0
        self.writes=0
        self.audit=[]
    def count(self,tool):
        if self.ops>=self.max_ops:raise RuntimeError("Operation limit exceeded.")
        self.ops+=1
        self.audit.append({"time":time.strftime("%Y-%m-%d %H:%M:%S"),"tool":tool,"operation":self.ops})
    def list_files(self,relative="."):
        if not self.permissions["list"]:raise PermissionError("List permission denied.")
        self.count("list_files")
        p=self.path(relative)
        if not p.exists():return []
        return sorted(str(x.relative_to(self.root).as_posix()) for x in p.iterdir())
    def read_file(self,relative):
        if not self.permissions["read"]:raise PermissionError("Read permission denied.")
        self.count("read_file")
        p=self.path(relative)
        if not p.is_file():raise FileNotFoundError(relative)
        if p.stat().st_size>self.max_file_bytes:raise ValueError("File exceeds read limit.")
        return p.read_text(encoding="utf-8")
    def write_file(self,relative,content):
        if not self.permissions["write"]:raise PermissionError("Write permission denied.")
        data=str(content).encode()
        if len(data)>self.max_file_bytes:raise ValueError("File exceeds size limit.")
        if self.writes+len(data)>self.max_write_bytes:raise RuntimeError("Write byte limit exceeded.")
        self.count("write_file")
        p=self.path(relative)
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(data)
        self.writes+=len(data)
        return {"path":p.relative_to(self.root).as_posix(),"bytes":len(data)}
    def rollback(self):
        for p in sorted(self.root.rglob("*"),reverse=True):
            if p.is_file():p.unlink()
            elif p.is_dir() and p!=self.root:p.rmdir()
        for rel,data in self.snapshot.items():
            if rel=="__dirs__":continue
            p=self.root/rel
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(data)
        self.audit.append({"time":time.strftime("%Y-%m-%d %H:%M:%S"),"tool":"rollback","operation":self.ops+1})
    def execute(self,tasks):
        queue=deque(tasks)
        results=[]
        self.begin()
        try:
            while queue:
                task=queue.popleft()
                if not isinstance(task,dict):raise ValueError("Each task must be an object.")
                tool=task.get("tool")
                args=task.get("args",{})
                if tool=="list_files":result=self.list_files(args.get("path","."))
                elif tool=="read_file":result=self.read_file(args["path"])
                elif tool=="write_file":result=self.write_file(args["path"],args.get("content",""))
                else:raise PermissionError(f"Tool not permitted: {tool}")
                results.append({"tool":tool,"status":"success","result":result})
            return {"status":"success","tasks":results,"audit":self.audit,"rolled_back":False}
        except Exception as error:
            self.rollback()
            return {"status":"failed","error":str(error),"tasks":results,"audit":self.audit,"rolled_back":True}
def demo_tasks():
    return [{"tool":"write_file","args":{"path":"workspace/agent_note.txt","content":"Generated inside controlled sandbox.\n"}},{"tool":"write_file","args":{"path":"workspace/result.txt","content":"Sandbox task completed.\n"}},{"tool":"list_files","args":{"path":"workspace"}},{"tool":"read_file","args":{"path":"workspace/agent_note.txt"}}]
def run_demo(root):
    shutil.rmtree(root,ignore_errors=True)
    sb=Sandbox(root,max_ops=10,max_write_bytes=2048,max_file_bytes=1024)
    result=sb.execute(demo_tasks())
    print("AI AGENT SANDBOX")
    print("="*60)
    print("Status:",result["status"])
    print("Tasks:",len(result["tasks"]))
    print("Operations:",len(result["audit"]))
    print("Rollback:",result["rolled_back"])
    for item in result["tasks"]:print(item["tool"],item["status"])
    return result
def main():
    parser=argparse.ArgumentParser(prog="ai_agent_sandbox")
    parser.add_argument("--root",default="agent_sandbox")
    parser.add_argument("--tasks",default="")
    parser.add_argument("--demo",action="store_true")
    parser.add_argument("--max-ops",type=int,default=25)
    parser.add_argument("--max-write-bytes",type=int,default=65536)
    parser.add_argument("--max-file-bytes",type=int,default=65536)
    parser.add_argument("--json",dest="json_file",default="")
    args=parser.parse_args()
    if args.demo or not args.tasks:
        report=run_demo(Path(args.root))
    else:
        tasks=json.loads(Path(args.tasks).read_text(encoding="utf-8"))
        if not isinstance(tasks,list):raise ValueError("Task file must contain a list.")
        sb=Sandbox(args.root,args.max_ops,args.max_write_bytes,args.max_file_bytes)
        report=sb.execute(tasks)
        print("AI AGENT SANDBOX")
        print("="*60)
        print("Status:",report["status"])
        print("Tasks:",len(report["tasks"]))
        print("Rollback:",report["rolled_back"])
        if report["status"]=="failed":print("Error:",report["error"])
    if args.json_file:Path(args.json_file).write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
if __name__=="__main__":main()
