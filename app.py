import sys
import json
import math
from datetime import datetime, timedelta
import psycopg2
from flask import request
from flask_cors import CORS
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import MetaData
from sqlalchemy_utils import database_exists, create_database
from nanoid import generate
from random import *

#import classes
sys.path.insert(0, 'classes')
from project import Project
from alcModels import alcProject, alcUser, alcProjectUser, alcFile, Base
from dataseed import fakeNames, fakeProjectNames, fileMimeTypes

from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy import text

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

db_string = "postgresql://postgres:[PASSWORD]@localhost:5432/ixassignflask"

# Flask is case sensitive with routing 
@app.route("/project/projects/<string:id>", methods=['GET'])
def project(id):
    #WITH SQLALCHEMY

    db = create_engine(db_string) 
    session = Session(db) 

    stmt = select(alcProject).where(alcProject.Id == id) 
    _project = Project()

    for project in session.scalars(stmt):
        _project.id=str(project.Id)
        _project.name=str(project.Name)
        _project.files=[]
        _project.users=[]
        
        if project.Files:
            for file in project.Files:
                _project.files.append({
                    "id": str(file.Id),
                    "name": str(file.Name),
                    "type": str(file.Type),
                    "filePath": str(file.FilePath)
                })

        if project.Users:
            for user in project.Users:
                _project.users.append({
                    "id": str(user.Id),
                    "name": str(user.Name),
                    "email": str(user.Email),
                })

    return json.dumps({
        "status": 200,
        "results": _project.__dict__
    }) 

@app.route("/Project/Projects", methods=['GET'])
def projects():
    #WITHOUT SQLALCHEMY

    db = create_engine(db_string)

    start = request.args.get('start')
    size = request.args.get('size')
    filterstring = request.args.get("filters")
    sortingstring = request.args.get("sorting")

    intSize = 0

    if size:
        intSize = int(size)

    if filterstring:
        filters = json.loads(filterstring)

    if sortingstring:
        sorting = json.loads(sortingstring)

    sql = "SELECT * FROM public.\"Projects\" "

    filter = ""

    if filters and len(filters) > 0 and filters[0]["id"] and filters[0]["value"]:
        match filters[0]["id"]:
            case "name":
                filter = " where \"Name\" like '{}%' ".format(filters[0]["value"])
                #sql = sql + " where \"Name\" like '{}%' ".format(filters[0]["value"])

    sql = sql + filter

    order_by = " order by \"StartDate\" desc "

    if sorting and len(sorting) > 0 and sorting[0]["id"]:
        match sorting[0]["id"]:
            case "name":
                order_by = " order by \"Name\" {} ".format("desc" if sorting[0]["desc"] else "asc")
            case "startDate":
                order_by = " order by \"StartDate\" {} ".format("desc" if sorting[0]["desc"] else "asc")

    sql = sql + order_by

    if size:
        sql = sql + " limit {} ".format(size)

    if start and size:
        sql = sql + " offset {} ".format(int(start) * int(size))

    _projects = []
    totalRecords = 0 

    with db.connect() as conn: 
        result_set = conn.execute(text(sql)) 
        totalResults = conn.execute(text("SELECT COUNT(*) FROM public.\"Projects\" " + filter)) 

        for r in result_set:
            _project = Project()
            _project.name = r.Name 
            _project.id = str(r.Id) 
            _project.startDate = str(r.StartDate) 
            _projects.append(_project.__dict__)

        for total in totalResults:
            totalRecords = total.count

    return json.dumps({
        "status": 200,
        "results": { 
            "records": _projects,
            "totalPages" : math.ceil(totalRecords/intSize),
            "totalRecords" : totalRecords
        },
    }) 


if __name__ == "__main__":

    db = create_engine(db_string, echo=True)
    is_database_exists = database_exists(db.url)

    if not database_exists(db.url):
        create_database(db.url)

    if not is_database_exists:
        Base.metadata.create_all(db)

        with Session(db) as session:

            alcUsers = []
            alcProjects = []
            alcProjectUsers = []

            for userName in fakeNames:
                trimmedName = userName.replace(" ", "")
                _user = alcUser(
                    Id = generate(),
                    Name = userName,
                    Email = "{}@sqlflask.com".format(trimmedName)
                )
                
                alcUsers.append(_user)

            for projectName in fakeProjectNames:
                _project = alcProject(
                    Id = generate(),
                    Name = projectName,
                    StartDate = datetime.utcnow() + timedelta(days=-randint(1, 400), hours=-randint(1, 100), minutes=-randint(1, 59))
                )
                
                _project.Files = []

                for fileType in fileMimeTypes:
                    _file = alcFile(
                        Id = generate(),
                        Name = "{}_{}".format(projectName, fileType.replace("/", "_")),
                        FilePath = "https://via.placeholder.com/{}x{}".format(randint(100, 200), randint(40, 80)),
                        Type = fileType
                    )

                    _project.Files.append(_file)

                _project.Users = []
                for i in range(1, 16):
                    _projectUser = alcUsers[randint(0, len(alcUsers)-1)]
                    _alcProjectUser = alcProjectUser(
                        Id = generate(),
                        UserId = _projectUser.Id,
                        ProjectId = _project.Id
                    )

                alcProjects.append(_project)

            session.add_all(alcUsers)
            session.add_all(alcProjects)
            session.commit()


            for _alcProject in alcProjects:
                for i in range(1, 16):
                    _projectUser = alcUsers[randint(0, len(alcUsers)-1)]
                    _alcProjectUser = alcProjectUser(
                        Id = generate(),
                        UserId = _projectUser.Id,
                        ProjectId = _alcProject.Id
                    )

                    alcProjectUsers.append(_alcProjectUser)

            session.add_all(alcProjectUsers)
            session.commit()

    app.run(host="0.0.0.0", port=6005, debug=True)
