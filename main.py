from GUI import search_window
from DataBase import DB_connect
from searcher import Searcher
CONSOLE_MODE=False
if __name__ == "__main__":
    session = DB_connect("database")

    #no. of documents = 37497
    #no. of unique tokens= 570248
    # indexing=indexer(session)
    # indexing.start_indexing()

    # indexing.show_page_content()
    # indexing.calculate_tf_idf()
    # indexing.show_index_content()
    # indexing.show_token_content()
    if (CONSOLE_MODE):
        #session.cursor().execute("CREATE INDEX pid_index ON indexing(page_id);")
        #session.cursor().execute("DROP INDEX tf_index ;")
        searching = Searcher(session.cursor(), "Informatics")
        searching = Searcher(session.cursor(), "Mondego")
        searching = Searcher(session.cursor(), "Irvine")
        searching = Searcher(session.cursor(), "artificial intelligence")
        searching=  Searcher(session.cursor(),"computer science")
        #
        #
        #


    else:
        ui=search_window(session)
        ui.run()
    session.close()



