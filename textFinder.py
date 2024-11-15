import tkinter as tk
from tkinter import filedialog

import os
import glob

from settings import Settings

class AppWindow():
    results_per_target = None       # Cumulating matches per target word
    matches = {}                    # {'target word' : [files that had a match]}
    search_folder = "./"            # Root folder to start search from
    searched_files = []             # Short paths of files that were checked for target word(s)
    result_string = ""              # Displayed result text. Easy to copy to clipboard.
    default_folder = "./"           # Path to open with askDir() and askCssFile()
    settings : Settings = None      # Config class

    def __init__(self, master, settings:Settings):
        self.settings = settings
        self.root = master
        master.geometry("600x400")
        master.update()
        

        canvas = tk.Canvas(master,bd=0,border=0,highlightthickness=0)
        canvas.pack(fill='both',expand=True,padx=30,pady=20)

        left_canvas = tk.Canvas(canvas,bd=0,border=0,highlightthickness=0)
        left_canvas.place(x=0,relwidth=0.5,relheight=1)
        right_canvas = tk.Canvas(canvas,bd=0,border=0,highlightthickness=0)
        right_canvas.place(relx=0.5,relwidth=0.5,relheight=1)

        split_line = tk.Frame(left_canvas,background="grey")
        split_line.pack(side="right",fill="y",padx=10)

        ############################################
        # Target word(s)
        title_frame_target = tk.Frame(left_canvas)
        title_frame_target.pack(fill='x',pady=(20,0))
        target_title = tk.Label(title_frame_target,text="Target text", font=('Arial',16))
        target_title.pack(side="left")

        self.target_css = tk.IntVar()
        search_css = tk.Checkbutton(left_canvas, text="Target all classes and IDs of a CSS file", var=self.target_css, onvalue=1, offvalue=0, command=self.onTargetCssChanged)
        search_css.pack()

        f3 = tk.Frame(left_canvas)
        f3.pack()

        # Single word
        self.f3_target_word = tk.Frame(f3)
        self.f3_target_word.pack()
        target_text = tk.Label(self.f3_target_word, text="Target text:")
        target_text.pack(side="left")
        self.target_word = tk.StringVar()
        search_entry = tk.Entry(self.f3_target_word,textvariable=self.target_word)
        search_entry.pack(side="right")

        # Css file 
        self.f3_css = tk.Frame(f3)
        self.f3_css.pack()
        self.css_file = tk.StringVar()
        self.css_file.trace_add('write',self.onCssFileChanged)
        
        ask_dir_b = tk.Button(self.f3_css, text="Select CSS File", command=self.askCssFile)
        ask_dir_b.pack()
        
        self.css_file_entry = tk.Entry(self.f3_css, textvariable=self.css_file)
        self.css_file_label = tk.Label(self.f3_css, text="no file")
        self.css_file_label.pack()

        self.f3_css.pack_forget()

        ############################################
        # Seach folder
        title_frame = tk.Frame(left_canvas)
        title_frame.pack(fill='x',pady=(20,0))
        folder_title = tk.Label(title_frame,text="Search from Folder", font=('Arial',16))
        folder_title.pack(side="left")

        f1 = tk.Frame(left_canvas)
        f1.pack()
        self.search_folder = tk.StringVar()
        self.search_folder.trace_add('write',self.onSearchChanged)

        ask_dir_b = tk.Button(f1, text="Set Folder", command=self.askDir)
        ask_dir_b.pack()
        
        self.folder_entry = tk.Entry(f1, textvariable=self.search_folder)
        self.search_folder_label = tk.Label(left_canvas, text="Folder not set")
        self.search_folder_label.pack()

        self.recursive_int = tk.IntVar()
        recursive_cb = tk.Checkbutton(left_canvas,text="Recursive search",variable=self.recursive_int, onvalue=1, offvalue=2)
        recursive_cb.pack()

        ############################################
        # Search
        title_frame_search = tk.Frame(left_canvas)
        title_frame_search.pack(fill='x',pady=(20,0))
        search_title = tk.Label(title_frame_search,text="Search in files", font=('Arial',16))
        search_title.pack(side="left")

        f2 = tk.Frame(left_canvas)
        f2.pack()
        
        extension_label = tk.Label(f2, text="with File Extension")
        extension_label.pack(side="left")
        self.extensions = tk.StringVar()
        extension_entry = tk.Entry(f2, textvariable=self.extensions)
        extension_entry.pack(side="right")

        start_b = tk.Button(left_canvas, text="Search", command=self.startSearch)
        start_b.pack()

        ############################################
        # Result
        title_frame_result = tk.Frame(right_canvas)
        title_frame_result.pack(fill='x',pady=(20,0))
        result_title = tk.Label(title_frame_result,text="Result", font=('Arial',16))
        result_title.pack(side="left")
        

        f_result_optional = tk.Frame(right_canvas)
        f_result_optional.pack()

        f_type_selection = tk.Frame(f_result_optional)
        f_type_selection.pack()

        self.result_type_selection = tk.StringVar(value="matches")
        self.result_type_selection.trace_add("write", self.onResultTypeSelectionChanged)
        result_type_0 = tk.Radiobutton(f_type_selection, text="Show matches", value="matches", variable=self.result_type_selection)
        result_type_1 = tk.Radiobutton(f_type_selection, text="Show searched files", value="files", variable=self.result_type_selection)
        result_type_0.pack(side='left')
        result_type_1.pack(side='left')


        self.show_only_misses = tk.IntVar()
        self.show_only_misses_cb = tk.Checkbutton(
            f_result_optional,
            text="Show No Matches only",
            variable=self.show_only_misses,
            onvalue=1,
            offvalue=0,
            command=self.updateResultString)
        self.show_only_misses_cb.pack(side='left')

        copy_row = tk.Frame(right_canvas)
        copy_row.pack(fill='x')
        copy_results_b = tk.Button(copy_row, text="Copy to Clipboard", command=self.copyResultsToClipBoard)
        copy_results_b.pack(pady=(0,20),side="right")
        
        self.results_tb = tk.Text(right_canvas)
        self.results_tb.pack(fill='x')
    
        ############################################
        # Set Default Settings from Config
        self.setDefaultValuesFromConfig()

        return

    def onTargetCssChanged(self):
        if self.target_css.get() == 1:
            self.f3_target_word.pack_forget()
            self.f3_css.pack()
        else:
            self.f3_target_word.pack()
            self.f3_css.pack_forget()
        return

    def onSearchChanged(self, *args):
        self.search_folder_label.config(text=self.getSearchFolder())
        return

    def onCssFileChanged(self, *args):
        self.css_file_label.config(text=self.css_file.get())
        return

    def onResultTypeSelectionChanged(self, *args):
        if self.getResultTypeSelection() == "matches":
            self.show_only_misses_cb.pack(side='left')
        elif self.getResultTypeSelection() == "files":
            self.show_only_misses_cb.pack_forget()
        self.updateResultString()
        return

    def onCloseWindow(self):
        # Set current values from app to config for saving
        print("onCloseWindow")
        default_search_folder = str(self.getDefaultFolder())
        recursive_search = self.getRecursiveInt()
        extensions = self.getExtensions()
        try:
            self.settings.updateFromApp(default_search_folder, recursive_search, extensions)
        except TypeError as e:
            print("error:",e)
            pass
        self.root.destroy()

    def getDefaultFolder(self):
        return self.default_folder
    def setDefaultFolder(self, folder):
        self.default_folder = folder
    def getRecursiveInt(self):
        return self.recursive_int.get()
    def setRecursiveInt(self, value):
        self.recursive_int.set(int(value))
    def getExtensions(self):
        return self.extensions.get()
    def setExtensions(self, value):
        self.extensions.set(str(value))
    def getSearchFolder(self):
        return self.search_folder.get()
    def getSearchedFiles(self):
        return self.searched_files
    def setSearchedFiles(self, files, use_short_path:bool):
        searched_files = files
        if use_short_path:
            searched_files =[ str(filepath).replace(self.getSearchFolder(),"") for filepath in files ]
        self.searched_files = searched_files
    def getResultTypeSelection(self):
        return self.result_type_selection.get()

    def setDefaultValuesFromConfig(self):
        print("setDefaultValuesFromConfig")
        self.setDefaultFolder(self.settings.getDefaultFolder())
        self.setRecursiveInt(self.settings.getDefaultRecursive())
        self.setExtensions(self.settings.getDefaultExtensions())

    def updateInfoWidget(self,t):
        self.results_tb.delete(1.0, tk.END)
        self.results_tb.insert(tk.END, t)

        return

    def askDir(self):
        folder = filedialog.askdirectory(initialdir=self.getDefaultFolder(), title="Search from folder") 
        if folder:
            self.folder_entry.delete(0,tk.END)
            self.folder_entry.insert(0,folder)
            self.setDefaultFolder(str(folder))
        else:
            return ""
        
    def askCssFile(self):
        file_types = (('CSS Files','*.css'),)
        file = filedialog.askopenfilename(initialdir=self.getDefaultFolder(), title="CSS File", filetypes=(file_types)) 
        if file:
            self.css_file_entry.delete(0,tk.END)
            self.css_file_entry.insert(0,file)
            parentpath = os.path.dirname(file)
            self.setDefaultFolder(parentpath)
        else:
            return ""

    def updateResultString(self):
        new_text = ""
        if self.getResultTypeSelection() == "matches":
            if self.show_only_misses.get() == 1:
                new_text = "No Matches for:"
                for k in self.matches:
                    if len(self.matches[k]) == 0:
                        new_text += "\n" + str(k)
            else:
                new_text = "Matches:\n---"
                count = 0
                for k in self.matches:
                    count += len(self.matches[k])
                    if len(self.matches[k]) > 0:
                        new_text += "\n" + str(k)
                        for v in self.matches[k]:
                            new_text += "\n" + v
                if count == 0:
                    new_text = "No Matches found"
        elif self.getResultTypeSelection() == "files":
            files = self.getSearchedFiles()
            new_text = "Searched Files:\n---"
            for f in files:
                new_text += "\n" + str(f)

        self.result_string = new_text
        self.updateInfoWidget(new_text)
        return

    def startSearch(self):
        print("startSearch - search folder: " + str(self.getSearchFolder()))
        p = self.getSearchFolder()
        if not os.path.isdir(p):
            self.updateInfoWidget("Search folder (" + str(p) +") not found")
            return
        
        extension = self.getExtensions()
        if not extension:
            self.updateInfoWidget("Needs an file Extension to look for (html or such)")
            return
        
        # Target word(s)
        target_words = []
        # One target word
        if self.target_css.get() == 0:
            if len(self.target_word.get()) == 0:
                self.updateInfoWidget("Needs a Target text to search for")
                return
            target_words = [self.target_word.get()]
        # Class names from CSS as target words
        else:
            if not os.path.isfile(self.css_file.get()):
                self.updateInfoWidget("CSS file was not found!)")
                return
            target_words = self.getTargetWordsFromCss()

        # Get all matching files from folder(s)
        if self.getRecursiveInt() == 1:
            search_prompt = p + "/**/*." + extension
            all_files = glob.glob(search_prompt, recursive=True)
        else:
            search_prompt = p + "/*." + extension
            all_files = glob.glob(search_prompt, recursive=False)
        self.setSearchedFiles(all_files, True)
        print("all_files",all_files)

        # Find matching target word(s) from files
        self.matches.clear()
        for target_word in target_words:
            self.results_per_target = []
            for filepath in all_files:
                self.checkFileForTargetText(filepath,target_word)
            # Target word matches -dict. 
            self.matches[target_word] = [*self.results_per_target]

        self.updateResultString()
        return


    def checkFileForTargetText(self,filepath,target_word):
        if os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                dfs = f.read()
                if target_word in dfs:
                    print("Target: '" + str(target_word) + "'" + " -> found in",filepath)
                    self.results_per_target.append(str(filepath).replace(self.getSearchFolder(),""))
        return
    
    def getTargetWordsFromCss(self):
        # Get class names from CSS file, return as target words
        # Class name ends in one of these letters
        ending_letters = [" ", ",", "{", ":", "\n"]
        print("ending_letters:",ending_letters)
        dot_separated = None
        class_names = []
        # Get CSS text, separate to classes (".")
        with open(self.css_file.get(), 'r') as f:
            dot_separated = f.read().split(".")
        raw_text_parts = dot_separated.copy()
        # Separate IDs ("#")
        for part in dot_separated:
            if "#" in part:
                new_chunks = part.split("#")[1:]
                for c in new_chunks:
                    raw_text_parts.append(c)

        if raw_text_parts:
            for part in raw_text_parts:
                #print("---Checking: '"+str(part)+"'")
                n = ''
                i = -1
                # Find ending letter of the class name | get first occurrance
                for n2 in ending_letters:
                    i2 = part.find(n2)
                    if i2 != -1 and (i == -1 or i2 < i):
                        i = i2
                        n = n2
                # Split with ending letter to keep the class name
                if n != '':
                    new_classname = part.split(n)[0].strip()
                    if len(new_classname) > 0 and (new_classname[0].isalpha()):
                        #print("----> Ending with '"+str(n)+"' -> Got:",new_classname)
                        class_names.append(new_classname)
        print("CSS class names:",class_names)
        return class_names

    def copyResultsToClipBoard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(str(self.result_string))

root = tk.Tk()
root.title = "Text Finder"

settings = Settings()
app = AppWindow(root, settings)
root.protocol("WM_DELETE_WINDOW", app.onCloseWindow)

root.mainloop()
