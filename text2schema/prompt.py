from typing import List, Optional

def prompt_req_analysis(task_disc: str, sample_data: Optional[str], aux_q: Optional[str] = None) -> str:
    return f"""
    You're a database design analyst. Based on the following task description, please list the capabilities that your designed database may need to support. You must only output a single list, corresponding to a specific functionality.

Task Description: {task_disc}

Output Format:
["capability-1", "capability-2", ...]

Only return a single list, with no additional explanation. All items in the list should be in **the same language** as is used by the Task Discription.
""" if sample_data is None else f"""
    You're a database design analyst. Based on the following task description and sample data, please list the capabilities that your designed database would be able to support. Note that the types of information your database can contain are strictly limited to what exists in the sample data—do not extend beyond that. You must only output a single list, corresponding to a specific functionality.

Task Description: {task_disc}
Sample Data: {sample_data}

Output Format:
["func1", "func2", ...]

Only return a single list, with no additional explanation. All items in the list should be in **the same language** as is used by the Task Discription.
"""

def prompt_ER(task_disc: str, sample_data: Optional[str], reqs: List[str], aux_q: Optional[str] = None) -> str:
    return f"""
    You are a data analyst. Please design an ER diagram based on the following task description and functional requirements. Please output:

[1]A JSON-format description of the ER diagram, which should be a dict.

[2]An executable Python code snippet that uses graphviz for visualization.

[3]Combine the above two items into a single dict.

Notes:
(1) In the ER diagram, enclose entities with rectangles, attributes with ellipses, and relationships with diamonds.
(2) Label the edges between relationships and entities with the type of association, including 1, N, M, etc.
(3) All names in your ER diagram design should be in **the same language** as is used by Functional Requirements.
(4) Save the generated picture to "temp/ER.pdf", follow exactly the path.
{("(5)" + aux_q) if (isinstance(aux_q, str) and len(aux_q) > 0) else "Note End..."}

[Task Description]{task_disc}.

[Functional Requirements]{reqs}

Return format example:
```
    {"{"}
        "json_ER": {"{"} "entities": [ {"{"} "name": "Project", "attributes": [ "ProjectID", "ProjectName", "Status", "Progress", "Budget", "ActualCost", "StartDate", "EndDate", "ParentProjectID", "RiskAssessment", "ApprovalProcess" ] {"}"}, . . .], "relationships": [ {"{"} "from": "Project", "to": "SubProject", "label": "contains" {"}"}, {"{"} "from": "Project", "to": "Team", "label": "has" {"}"}, . . . ]{"}"},
        "code_ER": from graphviz import Digraph dot = Digraph() dot.attr(fontname='SimSun') dot.attr('node', shape='box', fontname='SimSun') entities = ['Project', 'SubProject', 'Team', 'Employee', 'ProjectMember', 'Task', 'ProjectDependency', 'BudgetRecord', 'Document', 'MeetingNote'] for entity in entities: dot.node(entity) dot.attr('node', shape='ellipse', fontname='SimSun') attributes = {"{"} 'Project': ['ProjectID', 'ProjectName', 'Status', 'Progress', 'Budget', 'ActualCost', 'StartDate', 'EndDate'], 'SubProject': ['SubProjectID', 'ParentProjectID'], 'Team': ['TeamID', 'TeamName', 'Department'], 'Employee': ['EmployeeID', 'Name', 'Department'], 'ProjectMember': ['Role'], 'Task': ['TaskID', 'TaskName', 'StartDate', 'EndDate'], 'BudgetRecord': ['Stage', 'BudgetAmount', 'ActualAmount'], 'Document': ['DocumentID', 'DocumentType', 'FilePath'], 'MeetingNote': ['MeetingID', 'Content'] {"}"} for entity, attrs in attributes.items(): for attr in attrs: attr_node = f'{"{"}entity{"}"}_{"{"}attr{"}"}' dot.node(attr_node, attr) dot.edge(entity, attr_node) dot.attr('node', shape='diamond', fontname='SimSun') relations = [ ('Project', 'SubProject', 'has- subproject', '1', 'N'), ('Project', 'Team', 'has- team', 'N', 'M'), ('Team', 'ProjectMember', 'includes- member', '1', 'N'), ('Employee', 'ProjectMember', 'is- member', '1', 'N'), ('ProjectMember', 'Project', 'assigned- to', 'N', '1'), ('Project', 'Task', 'has- task', '1', 'N'), ('Task', 'Employee', 'assigned- to', 'N', '1'), ('Project', 'ProjectDependency', 'has- dependency', '1', 'N'), ('ProjectDependency', 'Project', 'depends- on', 'N', '1'), ('Project', 'BudgetRecord', 'has- budget', '1', 'N'), ('Project', 'Document', 'has- documents', '1', 'N'), ('Project', 'MeetingNote', 'has- meetings', '1', 'N') ] for src, tgt, label, card_src, card_tgt in relations: rel_node = f'rel_{"{"}label{"}"}' dot.node(rel_node, label) dot.edge(src, rel_node, label=card_src) dot.edge(rel_node, tgt, label=card_tgt) dot.render('temp/ER', format='pdf', cleanup=True) print('Finished painting the ER ...')
```
Only return one dict without any additional explanation.
""" if sample_data is None else f"""
    You are a data analyst. Please design an ER diagram based on the following task description, sample data, and functional requirements. Please output:

[1] A JSON-format description of the ER diagram as a dict.

[2] An executable Python code snippet using graphviz for visualization.

[3] Combine the above two items into a single dict.

Notes:
(1) Please note that all types of information in your designed database must exist in the sample data; no additional extensions are allowed.
(2) In the ER diagram, enclose entities with rectangles, attributes with ellipses, and relationships with diamonds.
(3) Label the edges between relationships and entities with the type of association, including 1, N, M, etc.
(4) All names in your ER diagram design should be in **the same language** as is used by Functional Requirements.
(5) Save the generated picture to "temp/ER.pdf", follow exactly the path.
{("(6)" + aux_q) if (isinstance(aux_q, str) and len(aux_q) > 0) else "Note End..."}

[Task Description] {task_disc}.

[Functional Requirements] {reqs}.

Return format example:
```
    {"{"}
        "json_ER": {"{"} "entities": [ {"{"} "name": "Project", "attributes": [ "ProjectID", "ProjectName", "Status", "Progress", "Budget", "ActualCost", "StartDate", "EndDate", "ParentProjectID", "RiskAssessment", "ApprovalProcess" ] {"}"}, . . .], "relationships": [ {"{"} "from": "Project", "to": "SubProject", "label": "contains" {"}"}, {"{"} "from": "Project", "to": "Team", "label": "has" {"}"}, . . . ]{"}"},
        "code_ER": from graphviz import Digraph dot = Digraph() dot.attr(fontname='SimSun') dot.attr('node', shape='box', fontname='SimSun') entities = ['Project', 'SubProject', 'Team', 'Employee', 'ProjectMember', 'Task', 'ProjectDependency', 'BudgetRecord', 'Document', 'MeetingNote'] for entity in entities: dot.node(entity) dot.attr('node', shape='ellipse', fontname='SimSun') attributes = {"{"} 'Project': ['ProjectID', 'ProjectName', 'Status', 'Progress', 'Budget', 'ActualCost', 'StartDate', 'EndDate'], 'SubProject': ['SubProjectID', 'ParentProjectID'], 'Team': ['TeamID', 'TeamName', 'Department'], 'Employee': ['EmployeeID', 'Name', 'Department'], 'ProjectMember': ['Role'], 'Task': ['TaskID', 'TaskName', 'StartDate', 'EndDate'], 'BudgetRecord': ['Stage', 'BudgetAmount', 'ActualAmount'], 'Document': ['DocumentID', 'DocumentType', 'FilePath'], 'MeetingNote': ['MeetingID', 'Content'] {"}"} for entity, attrs in attributes.items(): for attr in attrs: attr_node = f'{"{"}entity{"}"}_{"{"}attr{"}"}' dot.node(attr_node, attr) dot.edge(entity, attr_node) dot.attr('node', shape='diamond', fontname='SimSun') relations = [ ('Project', 'SubProject', 'has- subproject', '1', 'N'), ('Project', 'Team', 'has- team', 'N', 'M'), ('Team', 'ProjectMember', 'includes- member', '1', 'N'), ('Employee', 'ProjectMember', 'is- member', '1', 'N'), ('ProjectMember', 'Project', 'assigned- to', 'N', '1'), ('Project', 'Task', 'has- task', '1', 'N'), ('Task', 'Employee', 'assigned- to', 'N', '1'), ('Project', 'ProjectDependency', 'has- dependency', '1', 'N'), ('ProjectDependency', 'Project', 'depends- on', 'N', '1'), ('Project', 'BudgetRecord', 'has- budget', '1', 'N'), ('Project', 'Document', 'has- documents', '1', 'N'), ('Project', 'MeetingNote', 'has- meetings', '1', 'N') ] for src, tgt, label, card_src, card_tgt in relations: rel_node = f'rel_{"{"}label{"}"}' dot.node(rel_node, label) dot.edge(src, rel_node, label=card_src) dot.edge(rel_node, tgt, label=card_tgt) dot.render('temp/ER', format='pdf', cleanup=True) print('Finished painting the ER ...')
    {"}"}
```
Only return one dict without any additional explanation.
"""

def prompt_schema(task_disc: str, sample_data: Optional[str], reqs: List[str], ER_json: dict, aux_q: Optional[str] = None) -> str:
    return f"""
    You are a data analyst. Based on the following ER diagram design, task description, and functional requirements, please design a schema and output it as a JSON-format dict. The schema should use **the original language** as is used in ER and conform to JSON syntax.

[Task Description] {task_disc}.

[Functional Requirements] {reqs}.

[ER Design] {ER_json}.

{("Additional Requirement: " + aux_q) if (isinstance(aux_q, str) and len(aux_q) > 0) else ""}

Return format example:
    ```
    {"{"}
    "tables": [
        {"{"}
            "name": "table_name",
            "description": "Description of this table's purpose",
            "columns": [
            {"{"}
                "name": "id",
                "type": "integer",
                "description": "Primary key",
                "constraints": {"{"} 
                    "primary_key": true|false,      
                    "nullable": true|false,       
                    "unique": true|false,             
                    "auto_increment": true|false,    
                    "foreign_key": {"{"}                
                        "table": "referenced_table", 
                        "column": "referenced_column"  
                    {"}"}
                {"}"}
            {"}"},
            {"{"}
                "name": "column_name",
                "type": "data_type",
                "description": "Description of this column",
                "constraints": {"{"}
                    "primary_key": true|false,     
                    "nullable": true|false,       
                    "unique": true|false,            
                    "auto_increment": true|false,  
                    "foreign_key": {"{"}               
                        "table": "referenced_table",  
                        "column": "referenced_column"  
                    {"}"}
                {"}"}
            {"}"},
            {"{"}
                "name": "foreign_key_column",
                "type": "integer",
                "description": "Foreign key to another table",
                "constraints": {"{"}
                    "primary_key": true|false,         
                    "nullable": true|false,           
                    "unique": true|false,              
                    "auto_increment": true|false,    
                    "foreign_key": {"{"}                  
                        "table": "referenced_table", 
                        "column": "referenced_column"  
                    {"}"}
                {"}"}
            {"}"}
            ]
        {"}"}
    ],
    "relationships": [
        {"{"}
            "name": "relationship_name",
            "type": "one_to_one|one_to_many|many_to_many",
            "description": "Description of this relationship",
            "from": {"{"}
                "table": "source_table",
                "column": "source_column"
            {"}"},
            "to": {"{"}
                "table": "target_table",
                "column": "target_column"
            {"}"},
            "junction_table": {"{"}
                "name": "junction_table_name",
                "source_column": "source_foreign_key",
                "target_column": "target_foreign_key"
            {"}"}
        {"}"}
    ]
    {"}"}
    ```
Only return one dict without any additional explanation.
""" if sample_data is None else f"""
    You are a data analyst. Based on the following ER diagram design, task description, sample data, and functional requirements, please design a schema and output it as a JSON-format dict describing the schema. Please note that all types of information in your designed database must exist in the sample data; no further extension is allowed.

[Task Description] {task_disc}.

[Sample Data] {sample_data}.

[Functional Requirements] {reqs}.

[ER Design] {ER_json}.

{("Additional Requirement: " + aux_q) if (isinstance(aux_q, str) and len(aux_q) > 0) else ""}

Return format example:
    ```
    {"{"}
    "tables": [
        {"{"}
            "name": "table_name",
            "description": "Description of this table's purpose",
            "columns": [
            {"{"}
                "name": "id",
                "type": "integer",
                "description": "Primary key",
                "constraints": {"{"} 
                    "primary_key": true|false,      
                    "nullable": true|false,       
                    "unique": true|false,             
                    "auto_increment": true|false,    
                    "foreign_key": {"{"}                
                        "table": "referenced_table", 
                        "column": "referenced_column"  
                    {"}"}
                {"}"}
            {"}"},
            {"{"}
                "name": "column_name",
                "type": "data_type",
                "description": "Description of this column",
                "constraints": {"{"}
                    "primary_key": true|false,     
                    "nullable": true|false,       
                    "unique": true|false,            
                    "auto_increment": true|false,  
                    "foreign_key": {"{"}               
                        "table": "referenced_table",  
                        "column": "referenced_column"  
                    {"}"}
                {"}"}
            {"}"},
            {"{"}
                "name": "foreign_key_column",
                "type": "integer",
                "description": "Foreign key to another table",
                "constraints": {"{"}
                    "primary_key": true|false,         
                    "nullable": true|false,           
                    "unique": true|false,              
                    "auto_increment": true|false,    
                    "foreign_key": {"{"}                  
                        "table": "referenced_table", 
                        "column": "referenced_column"  
                    {"}"}
                {"}"}
            {"}"}
            ]
        {"}"}
    ],
    "relationships": [
        {"{"}
            "name": "relationship_name",
            "type": "one_to_one|one_to_many|many_to_many",
            "description": "Description of this relationship",
            "from": {"{"}
                "table": "source_table",
                "column": "source_column"
            {"}"},
            "to": {"{"}
                "table": "target_table",
                "column": "target_column"
            {"}"},
            "junction_table": {"{"}
                "name": "junction_table_name",
                "source_column": "source_foreign_key",
                "target_column": "target_foreign_key"
            {"}"}
        {"}"}
    ]
    {"}"}
    ```
Only return one dict without any additional explanation.
"""