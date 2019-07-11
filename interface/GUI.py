from tkinter import *
from searcher import Searcher
from DataBase import DB_connect
from searcher import URLS_DISPLAYED
class search_window:
    '''show the graphic window for taking user's input and dispaly the results
    in anothr window. Users are able to view 10 results at a time. '''
    def __init__(self,session):
        self.query=None
        self.root=Tk()
        self.session = session

    def config_main_window(self):
        self.root.title("121 Search Engine")
        self.root.geometry('350x200')
        #self.root.columnconfigure(1, pad=3)
        l1 = Label(self.root, text="Please enter query: ")

        l1.pack(fill=X,pady=20)
        myString=StringVar()
        enter = Entry(self.root, textvariable=myString, width=10)

        enter.pack(fill=X,padx=10)

        def clicked():
            self.query=myString.get()
            self._config_result_window()
        btn = Button(self.root, text="Search", command=clicked)
        btn.pack(pady=10)
    def _config_result_window(self):
        self.subroot = Toplevel(self.root)
        self.subroot.title("Results from searching query: "+self.query)
        self.subroot.geometry('600x700')
        self._results_generator()
        self.subroot.mainloop()
    def _results_generator(self):
        sep = "------------------------------------------------------\n"

        def _update_next(is_next: bool):
            if is_next:
                s.read_pos += URLS_DISPLAYED
            else:
                s.read_pos -= URLS_DISPLAYED
            new_content = s.results_gen()
            T.delete('1.0', END)
            for url, snippet in new_content:
                T.insert("end", url + '\n' + sep + snippet + '\n\n\n')
            btn = Button(self.subroot, text="Next Page", command=lambda: _update_next(True))
            btn_p = Button(self.subroot, text="Previous Page", command=lambda: _update_next(False))
            T.window_create(END, window=btn_p)

            T.window_create(END, window=btn)
            T.insert(END, "\n")
        if (self.query!=None):


            cursor=self.session.cursor()
            s=Searcher(cursor,self.query)
            #displayed_content=[('a','b')]
            displayed_content=s.results_gen()
            S=Scrollbar(self.subroot)
            T=Text(self.subroot)
            btn = Button(self.subroot, text="Next Page", command=lambda:_update_next(True))
            btn_p=Button(self.subroot, text="Previous Page", command= lambda:_update_next(False))
            S.pack(side=RIGHT, fill=Y)
            T.pack(side=LEFT, fill=BOTH, expand=1)
            #btn.pack(side=BOTTOM)
            S.config(command=T.yview)
            T.config(yscrollcommand=S.set)
            T.config(state=NORMAL)

            T.insert(END,"Number of results found: "+str(len(s.scores))+'\n')
            for url,snippet in displayed_content:
                T.insert(END,url+'\n'+sep+snippet+'\n\n\n')
            T.window_create(END, window=btn_p)

            T.window_create(END, window=btn)

            # T.insert(END, "\n")
           # self.subroot.mainloop()




    def run(self):
        self.config_main_window()
        self.root.mainloop()