from fastapi import FastAPI,HTTPException
from pymongo import MongoClient
import os
from pydantic import BaseModel
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
client = MongoClient(os.getenv("MONGO_URI"))
db=client.taskdb

@app.get("/")
def read_root():
    return {"Hello":"world"}

class Task(BaseModel):
    title:str
    description:str

@app.post("/tasks")
def create_task(task:Task):
    task_id=db.tasks.insert_one(task.dict()).inserted_id
    return {"id":str(task_id),"message":"task created"}

@app.get("/tasks")
def get_tasks():
    tasks=list(db.tasks.find({},{"_id":1,"title":1,"description":1}))
    for t in tasks:
        t["id"]=str(t["_id"])
        del t["_id"]
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id:str):
    task=db.tasks.find_one({"_id":ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404,detail="task not found")
    task["id"]=str(task["_id"])
    del task["_id"]
    return task
    
@app.put("/tasks/{task_id}")
def update_task(task_id:str,task:Task):
    result = db.tasks.update_one(
        {"_id":ObjectId(task_id)},
        {"$set":task.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404,detail="task not found")
    return {"message":"Task Updated"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id:str):
    result = db.tasks.delete_one({"_id":ObjectId(task_id)})
    
    if result.deleted_count==0:
        raise HTTPException(status_code=404,detail="task not found")
    return {"message":"task deleted"}