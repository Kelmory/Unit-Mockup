# Unit Generator
A random mock generator for creating units for degrees. Could be used to generate data for Neo4j.

## Usage
The json files will be generated directly into the pwd. To configure the probability, etc., make changes on the captilized-character only consts.
```shell
python generator.py
```

## Neo4j graph creation
Start a python http server using `python -m http.server 8080` at the parent directory of JSON data files. Then in the Neo4j browser, execute the following command:

```cypher
//Create graph - Degree
CALL apoc.load.json("http://localhost:8080/degrees.json")
YIELD value
MERGE (d:DEGREE {code:value.code, name:value.name, credits:value.credits})
RETURN d

//Create graph - Units
CALL apoc.load.json("http://localhost:8080/units.json") 
YIELD value
MERGE (c: Course {code: value.code, title: value.title, credit: value.credit, level: value.level}) 
WITH c, value
UNWIND value.prerequisites AS pre
UNWIND pre AS sole
MATCH (p1:Course {code:sole})
MERGE (p1)-[:IS_PREREQUISITE {condition:pre}]->(c)
WITH c, value
UNWIND value.prohibited AS proh
MATCH (p2:Course {code:proh})
MERGE (p2)-[:IS_PROHIBITION]->(c)
```
