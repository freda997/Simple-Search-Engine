import sqlite3
import os

def DB_connect(file_name):  # building the database and load all the url into pages
    DEFAULT_PATH = os.path.join(os.path.dirname(__file__), file_name+'.sqlite3')
    return sqlite3.connect(DEFAULT_PATH)


def create_table(cur):
    drop_all = """

   
    DROP TABLE IF EXISTS indexing;
    """
    pages_sql = """ 
                CREATE TABLE IF NOT EXISTS pages(
                    page_id INT NOT NULL,
                    url VARCHAR(2083) NOT NULL,
                    primary key(page_id)
                );

                 """
    token_sql = """ CREATE TABLE IF NOT EXISTS tokens(
                    token VARCHAR(300) NOT NULL,
                    doc_freq INT,
                    primary key(token)
                );
                """
    index_sql = """  CREATE TABLE IF NOT EXISTS indexing(
                    token VARCHAR(300) NOT NULL,
                    page_id INT NOT NULL,
                    token_freq INT,
                    tf_idf DOUBLE, 
                    PRIMARY KEY (token,page_id),
                    FOREIGN KEY (page_id) REFERENCES pages(page_id) ON DELETE CASCADE,
                    FOREIGN KEY (token) REFERENCES tokens(token) ON DELETE CASCADE);
                    
                    """
    trigger_sql = """
                CREATE TRIGGER IF NOT EXISTS incre_doc_freq BEFORE INSERT ON indexing
                 FOR EACH ROW 
                 WHEN NOT EXISTS (SELECT * FROM tokens WHERE token=new.token)  
                 BEGIN
                  INSERT INTO tokens VALUES (new.token,1);
                 END;
                  """
    trigger_sql2 = """
                        CREATE TRIGGER IF NOT EXISTS incre_doc_freq2 BEFORE INSERT ON indexing
                         FOR EACH ROW 
                         WHEN  EXISTS (SELECT * FROM tokens WHERE token=new.token)  
                         BEGIN
                          UPDATE tokens SET doc_freq=doc_freq+1 WHERE token=new.token;
                         END;
                          """
    cur.executescript(drop_all)
    cur.execute(token_sql)
    cur.execute(pages_sql)
    cur.executescript(index_sql)
    #cur.execute(trigger_sql)
    #cur.execute(trigger_sql2)