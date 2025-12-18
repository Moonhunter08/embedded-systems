class CSV_Interface:
    def __init__(self, filename):
        import _thread
        self.lock = _thread.allocate_lock()
        self.filename = filename
        self.impact_count = 0
        
        try:
            import os
            os.remove(self.filename)
        except OSError:
            pass

        self.write_row(['Time since boot (mm:ss:msms)', 'G-Force'])  # Write header
        

    def write_row(self, row):
        with self.lock:
            self.file = open(self.filename, 'a')
            line = ','.join(str(item) for item in row) + '\n'
            self.file.write(line)
            self.file.flush()
            self.file.close()

    def get_content(self):
        with self.lock:
            with open(self.filename, 'r') as file:
                return file.read()
