# FOR GUI
import tkinter as tk
# FOR MESSAGE BOXES
import tkinter.messagebox
# FOR COMBO BOXES
import tkinter.ttk
# FOR DATE PICKER
import tkcalendar
# FOR DATABASE
import sqlite3
# FOR COPYING OBJECTS
import copy
# FOR MEDICATION LOOKUP
import webbrowser
# FOR DATES COMPARISON
from datetime import datetime
# FOR PDF
import fpdf


# DATABASE CREATION AND MANAGEMENT
class DatabaseManager:
    def __init__(self):
        self.connection = sqlite3.connect('nurse_aid.db')
        self.cursor = self.connection.cursor()

    # CREATE TABLES
    def create_tables(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS resident (
                                id integer PRIMARY KEY,
                                first_name text,
                                last_name text,
                                dob text
                            )""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS medication (
                                id integer PRIMARY KEY,
                                name text,
                                other_name text,
                                resident_id integer,
                                notes text DEFAULT ' ',
                                FOREIGN KEY (resident_id) REFERENCES resident(id) 
                            )""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS medication_info (
                                id integer PRIMARY KEY,
                                expiry text,
                                quantity real,
                                strength real,
                                medication_type text,
                                notes text,
                                medication_id integer,
                                supplier text,
                                measurement text,
                                FOREIGN KEY (medication_id) REFERENCES medication(id) 
                            )""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS dose_info (
                                id integer PRIMARY KEY,
                                dose real,
                                measurement text,
                                frequency_per_day real,
                                regular_or_prn integer,
                                medication_info_id integer,
                                FOREIGN KEY (medication_info_id) REFERENCES medication_info(id) 
                            )""")

        self.connection.commit()

    # COLLECT RESIDENT IDENTIFIERS
    def collect_resident_identifiers(self):
        self.cursor.execute("SELECT id, first_name, last_name, dob FROM resident")
        self.connection.commit()
        return self.cursor.fetchall()

    # ADD RESIDENT TO DATABASE
    def add_resident_to_database(self, first_name, last_name, dob):
        self.cursor.execute("INSERT INTO resident (first_name, last_name, dob) VALUES (?, ?, ?)", (first_name,
                                                                                                   last_name, dob))
        self.connection.commit()

    # ADD MEDICATION TO DATABASE
    def add_medication_to_database(self, medication_name, medication_other_name, resident_id):
        self.cursor.execute("INSERT INTO medication (name, other_name, resident_id) VALUES (?, ?, ?)", (
            medication_name, medication_other_name, resident_id))
        self.connection.commit()

    # ADD MEDICATION INSTANCE TO DATABASE
    def add_medication_instance_to_database(self, instance_expiry, instance_quantity, instance_strength,
                                            instance_medication_type, instance_medication_id, instance_supplier,
                                            instance_measurement):
        self.cursor.execute("INSERT INTO medication_info (expiry, quantity, strength, medication_type, medication_id, "
                            "supplier, measurement) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (instance_expiry, instance_quantity,
                             instance_strength,
                             instance_medication_type,
                             instance_medication_id,
                             instance_supplier, instance_measurement))
        self.connection.commit()

    # ADD MEDICATION INSTANCE DOSE TO DATABASE
    def add_medication_instance_dose_to_database(self, dose_amount, dose_measurement, dose_frequency, dose_regularity,
                                                 dose_medication_info_id,):
        self.cursor.execute("INSERT INTO dose_info (dose, measurement, frequency_per_day, regular_or_prn,"
                            " medication_info_id) VALUES (?, ?, ?, ?, ?)",
                            (dose_amount,
                                dose_measurement,
                                dose_frequency,
                                dose_regularity,
                                dose_medication_info_id))
        self.connection.commit()

    # ADD MEDICATION NOTES TO DATABASE
    def add_medication_notes_to_database(self, notes_text_box, medication_id):
        self.cursor.execute('UPDATE medication SET notes=? WHERE id=?', [notes_text_box, medication_id])
        self.connection.commit()

    # COLLECT RESIDENT MEDICATION
    def collect_resident_medication(self, resident_id):
        self.cursor.execute("SELECT * FROM medication WHERE resident_id == (?);", (str(resident_id),))
        self.connection.commit()
        return self.cursor.fetchall()

    # COLLECT MEDICATION INSTANCES
    def collect_medication_instances(self, medication_id):
        self.cursor.execute("SELECT * FROM medication_info WHERE medication_id == (?);", (str(medication_id),))
        self.connection.commit()
        return self.cursor.fetchall()

    # COLLECT MEDICATION INSTANCE DOSES
    def collect_medication_instance_doses(self, medication_info_id):
        self.cursor.execute("SELECT * FROM dose_info WHERE medication_info_id == (?);", (str(medication_info_id),))
        self.connection.commit()
        return self.cursor.fetchall()

    # COLLECT QUANTITY AND STRENGTH
    def collect_quantity_and_strength(self, medication_info_id):
        self.cursor.execute("SELECT quantity, strength FROM medication_info WHERE id == (?);", (str(medication_info_id),
                                                                                                ))
        self.connection.commit()
        quantity_and_strength = self.cursor.fetchall()
        current_quantity = quantity_and_strength[0][0]
        current_strength = quantity_and_strength[0][1]
        return current_quantity, current_strength

    # COLLECT MEDICATIONS INSTANCES EXPIRY DATES
    def collect_medications_instances_expiry_dates(self, resident_id):
        self.cursor.execute("SELECT id FROM medication WHERE resident_id == (?);", (str(resident_id,)))
        medication_ids_owned_by_resident = self.cursor.fetchall()
        expiry_dates = []
        for medication_id in medication_ids_owned_by_resident:
            self.cursor.execute("SELECT expiry FROM medication_info WHERE medication_id == (?);", medication_id)
            for date in self.cursor.fetchall():
                expiry_dates.append(date[0])
        self.connection.commit()
        return expiry_dates

    # COLLECT MEDICATION IDS WHERE DATES MATCH
    def collect_medication_ids_where_dates_match(self, date):
        self.cursor.execute("SELECT medication_id FROM medication_info WHERE expiry == (?);", (date,))
        self.connection.commit()
        return self.cursor.fetchall()

    # COLLECT CURRENTLY SELECTED MEDICATION NAME
    def collect_medication_name(self, medication_id):
        self.cursor.execute("SELECT name FROM medication WHERE id == (?);", (str(medication_id),))
        self.connection.commit()
        return self.cursor.fetchall()

    # COLLECT MEDICATION NOTES
    def collect_medication_notes(self, medication_id):
        self.cursor.execute("SELECT notes FROM medication WHERE id == (?);", (str(medication_id),))
        self.connection.commit()
        return self.cursor.fetchall()[0][0]

    # MODIFY MEDICATION INSTANCE QUANTITY
    def modify_medication_instance_quantity(self, modify_stock_field, medication_info_id):
        self.cursor.execute('UPDATE medication_info SET quantity=? WHERE id=?', [float(modify_stock_field),
                                                                                 medication_info_id])
        self.connection.commit()


# PARENT CLASS FOR WINDOW CREATION AND MANAGEMENT
class WindowManager:
    def __init__(self, master, title, geometry, previous_window):
        self.master = master
        self.window = tk.Toplevel(self.master)
        self.window.geometry(geometry)
        self.window.iconbitmap(r"icon.ico")
        self.window.title(title)
        self.window.focus_force()
        self.window.resizable(False, False)
        self.window.protocol('WM_DELETE_WINDOW', self.on_exit)
        self.previous_window = previous_window

    # ON WINDOW EXIT
    def on_exit(self):
        self.window.destroy()
        if self.previous_window.title() == 'tk':
            self.previous_window.destroy()
        else:
            self.previous_window.deiconify()

    # CENTERS THE WINDOW
    def center_window(self, x, y):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (x / 2))
        y_coordinate = int((screen_height / 2) - (y / 2))
        self.window.geometry("{}x{}+{}+{}".format(x, y, x_coordinate, y_coordinate))

    # CREATE A BUTTON
    def make_button(self, text, command, state, pad_x, pad_y, side):
        button = tk.Button(master=self.window, text=text, command=command, state=state)
        button.pack(padx=pad_x, pady=pad_y, side=side)
        return button

    # CREATE A LISTBOX
    def make_listbox(self, height, width, pad_x, pad_y, side):
        listbox = tk.Listbox(master=self.window, width=width, height=height, exportselection=False,
                             highlightcolor='blue', highlightthickness=2, bd=4)
        listbox.pack(padx=pad_x, pady=pad_y, side=side)
        return listbox

    # CREATE A LABEL
    def make_label(self, text, pad_x, pad_y):
        label = tk.Label(master=self.window, text=text)
        label.pack(padx=pad_x, pady=pad_y)
        return label

    # CREATE AN ENTRY FIELD
    def make_entry_field(self):
        entry_field = tk.Entry(master=self.window)
        entry_field.pack()
        return entry_field

    # CREATE A DATE PICKER
    def make_date_picker(self, start_year):
        date_picker = tkcalendar.Calendar(master=self.window, selectmode='day', year=start_year)
        date_picker.pack()
        return date_picker

    # CREATE A SCALE
    def make_scale(self):
        scale = tk.Scale(master=self.window, orient='horizontal', activebackground='Blue',
                         to=1000, width=15, length=250, troughcolor='White', sliderlength=30, resolution=0.5)
        scale.pack()
        return scale

    # CREATE A COMBO BOX
    def make_combo_box(self, list_items):
        combo_box = tkinter.ttk.Combobox(master=self.window, state='readonly', values=list_items)
        combo_box.pack()
        return combo_box

    # CREATE A TEXT BOX
    def make_text_box(self, width, height):
        text_box = tk.Text(master=self.window, width=width, height=height)
        text_box.pack()
        return text_box

    # CREATE A MESSAGE BOX
    @staticmethod
    def make_message_box(title, message, icon):
        tk.messagebox.showinfo(title=title, message=message, icon=icon)


# CHILD WINDOWS OF WindowManager
class PrimaryWindow(WindowManager):
    def __init__(self, master, title, geometry, previous_window):
        super().__init__(master, title, geometry, previous_window)

        # WIDGETS
        WindowManager.make_button(self, text='Residents', command=self.show_resident_selection_window, state='active',
                                  pad_x=0, pad_y=20, side=tk.TOP)

    # BUTTON COMMANDS
    def show_resident_selection_window(self):
        self.window.withdraw()
        resident_selection_window = ResidentSelectionWindow(master=self.window, title='Resident Selection',
                                                            geometry='275x400', previous_window=self.window)
        resident_selection_window.center_window(x=275, y=400)


class ResidentSelectionWindow(WindowManager):
    def __init__(self, master, title, geometry, previous_window):
        super().__init__(master, title, geometry, previous_window)

        # WIDGETS
        # LIST BOXES AND BUTTONS
        self.resident_selection_listbox = WindowManager.make_listbox(self, width=95, height=19, pad_x=0, pad_y=0,
                                                                     side=tk.TOP)
        self.populate_resident_listbox()

        self.view_medications_button = WindowManager.make_button(self, text='View Medications',
                                                                 command=self.show_medication_window, state='active',
                                                                 pad_x=0, pad_y=5, side=tk.TOP)

        self.add_resident_button = WindowManager.make_button(self, text='Add Resident',
                                                             command=self.show_add_resident_window, state='active',
                                                             pad_x=0, pad_y=5, side=tk.TOP)
        # BINDINGS
        self.resident_selection_listbox.bind('<<ListboxSelect>>', self.resident_listbox_selected)

    # EVENT HANDLERS
    def resident_listbox_selected(self, event):
        print(event)
        self.resident_selection()

    def resident_selection(self):
        selected_resident_id = self.resident_selection_listbox.curselection()[0] + 1
        selected_resident_details = self.resident_selection_listbox.get(selected_resident_id - 1)
        return selected_resident_id, selected_resident_details

    # BUTTON COMMANDS
    def show_medication_window(self):
        try:
            self.resident_selection()
            self.window.withdraw()

            resident_medication_window = ResidentMedicationWindow(
                master=self.window, title=f'Medication List For {self.resident_selection()[1]}', geometry='1350x700',
                previous_window=self.window, resident_selection_window=self)
            resident_medication_window.center_window(x=1350, y=700)

        except IndexError:
            WindowManager.make_message_box(title='Error', message='Please select a resident before trying to view '
                                                                  'medications.', icon='error')

    def show_add_resident_window(self):
        self.window.withdraw()
        add_resident_window = AddResidentWindow(master=self.window, title='Add Resident', geometry='600x400',
                                                previous_window=self.window, resident_selection_window=self)
        add_resident_window.center_window(x=600, y=400)

    # RESIDENT SELECTION LIST BOX POPULATION
    def populate_resident_listbox(self):
        self.resident_selection_listbox.delete(first=0, last=tk.END)
        for i, resident in enumerate(DatabaseManager().collect_resident_identifiers()):
            # resident_id = resident[0]
            resident_first_name = resident[1]
            resident_last_name = resident[2]
            resident_dob = resident[3]
            self.resident_selection_listbox.insert(i, f"{resident_first_name} {resident_last_name} - {resident_dob}")


class AddResidentWindow(WindowManager):
    def __init__(self, master, title, geometry, previous_window, resident_selection_window):
        super().__init__(master, title, geometry, previous_window)

        self.resident_selection_window = resident_selection_window

        # WIDGETS
        WindowManager.make_label(self, text='First Name', pad_x=0, pad_y=0)
        self.first_name_field = WindowManager.make_entry_field(self)

        WindowManager.make_label(self, text='Last Name', pad_x=0, pad_y=0)
        self.last_name_field = WindowManager.make_entry_field(self)

        WindowManager.make_label(self, text='Select DOB', pad_x=0, pad_y=5)
        self.dob_date_picker = WindowManager.make_date_picker(self, start_year=2000)

        WindowManager.make_button(self, text='Add', command=self.add_resident_to_database, state='active', pad_x=0,
                                  pad_y=5, side=tk.TOP)

    # BUTTON COMMANDS
    def add_resident_to_database(self):
        if self.first_name_field.get().isalpha() and self.last_name_field.get().isalpha():
            DatabaseManager.add_resident_to_database(self=DatabaseManager(), first_name=self.first_name_field.get(),
                                                     last_name=self.last_name_field.get(),
                                                     dob=self.dob_date_picker.get_date())

            self.window.destroy()
            self.previous_window.deiconify()

            ResidentSelectionWindow.populate_resident_listbox(self=self.resident_selection_window)

            WindowManager.make_message_box(title='Success', message='Resident added to database.', icon='info')

        else:
            WindowManager.make_message_box(title="Error", message='Please fill in all fields correctly and try again.',
                                           icon='error')


class ResidentMedicationWindow(WindowManager):
    def __init__(self, master, title, geometry, previous_window, resident_selection_window):
        super().__init__(master, title, geometry, previous_window)

        self.resident_selection_window = resident_selection_window
        self.resident_selection_id = ResidentSelectionWindow.resident_selection(self.resident_selection_window)[0]
        self.resident_selection_details = ResidentSelectionWindow.resident_selection(
            self.resident_selection_window)[1]

        self.medication_ids = []
        self.selected_medication_id = ''

        self.medication_info_ids = []
        self.selected_medication_info_id = ''

        self.last_selected_medication_name = ''
        self.last_selected_medication_id = ''
        self.last_selected_medication_info_id = ''
        self.last_selected_medication_instance_index = ''

        self.medication_notes_window_open = False

        # WIDGETS
        # LABELS AND LIST BOXES
        WindowManager.make_label(self, text=self.resident_selection_details, pad_x=0, pad_y=5)

        self.medication_selection_listbox = WindowManager.make_listbox(self, width=95, height=20, pad_x=0, pad_y=5,
                                                                       side=tk.TOP)
        self.populate_medication_listbox()

        self.medication_instance_selection_listbox = WindowManager.make_listbox(self, width=95, height=20, pad_x=0,
                                                                                pad_y=0, side=tk.LEFT)

        self.medication_instance_dose_selection_listbox = WindowManager.make_listbox(self, width=95, height=20, pad_x=0,
                                                                                     pad_y=0, side=tk.RIGHT)
        # BUTTONS AND ENTRY FIELDS
        self.add_medication_button = WindowManager.make_button(self, text='Add Medication',
                                                               command=self.show_add_medication_window, pad_y=5,
                                                               pad_x=0, state='active', side=tk.TOP)

        self.add_medication_instance_button = WindowManager.make_button(
            self, text='Add Medication Instance', command=self.show_add_medication_instance_window,
            pad_y=5, pad_x=0, state='active', side=tk.TOP)

        self.add_medication_instance_dose_button = WindowManager.make_button(
            self, text='Add Medication Instance Dose', command=self.show_add_medication_instance_dose_window, pad_y=5,
            pad_x=0, state='active', side=tk.TOP)

        self.check_expiry_dates_button = WindowManager.make_button(
            self, text='Create Expiry Dates Report', command=self.create_expiry_date_pdf_report, pad_y=(30, 5),
            pad_x=0, state='active', side=tk.TOP)

        self.modify_medication_instance_stock_button = WindowManager.make_button(
            self, text='Modify Instance Stock', command=self.modify_instance_stock_level, pad_y=5, pad_x=0,
            state='active', side=tk.TOP)
        self.modify_medication_instance_stock_field = WindowManager.make_entry_field(self)

        self.lookup_medication_button = WindowManager.make_button(
            self, text='Lookup Medication', command=self.lookup_medication, pad_y=5, pad_x=0, state='active',
            side=tk.BOTTOM)

        self.show_medication_notes_button = WindowManager.make_button(
            self, text='View Medication Notes', command=self.show_medication_notes_window, pad_y=5, pad_x=0,
            state='active', side=tk.BOTTOM)

        # BINDINGS
        self.medication_selection_listbox.bind('<<ListboxSelect>>', self.medication_listbox_selected)
        self.medication_instance_selection_listbox.bind('<<ListboxSelect>>', self.medication_instances_listbox_selected)
        self.medication_selection_listbox.bind('<FocusOut>', self.clear_selected_medication_id)
        self.medication_instance_selection_listbox.bind('<FocusOut>', self.clear_selected_medication_info_id)

    # EVENT HANDLERS
    # MEDICATION LISTBOX EVENTS
    def medication_listbox_selected(self, event):
        print(event)
        self.medication_selection()

    def medication_selection(self):
        self.selected_medication_id = self.medication_ids[self.medication_selection_listbox.curselection()[0]]

        self.last_selected_medication_id = copy.copy(self.selected_medication_id)
        self.get_last_selected_medication_name()

        self.populate_medication_instance_listbox()
        self.medication_instance_dose_selection_listbox.delete(0, tk.END)

    def clear_selected_medication_id(self, event):
        print(event)
        self.selected_medication_id = ''

    # MEDICATION INSTANCES LISTBOX EVENTS
    def medication_instances_listbox_selected(self, event):
        print(event)
        self.medication_instance_selection()

    def medication_instance_selection(self):
        self.last_selected_medication_instance_index = self.medication_instance_selection_listbox.curselection()[0]

        self.selected_medication_info_id = self.medication_info_ids[
            self.medication_instance_selection_listbox.curselection()[0]]

        self.last_selected_medication_info_id = copy.copy(self.selected_medication_info_id)

        self.populate_medication_instance_dose_listbox()

    def clear_selected_medication_info_id(self, event):
        print(event)
        self.selected_medication_info_id = ''

    # BUTTON COMMANDS
    def show_add_medication_window(self):
        self.window.withdraw()

        add_medication_window = AddMedicationWindow(master=self.window,
                                                    title='Add Medication for ' + self.resident_selection_details,
                                                    geometry='600x400', previous_window=self.window,
                                                    selected_resident_id=self.resident_selection_id,
                                                    resident_medication_window=self)
        add_medication_window.center_window(600, 400)

    def show_add_medication_instance_window(self):
        if self.selected_medication_id:

            self.window.withdraw()

            currently_selected_medication_name = DatabaseManager.collect_medication_name(
                DatabaseManager(), self.selected_medication_id)[0][0]

            add_medication_instance_window = AddMedicationInstanceWindow(
                master=self.window, title=f'Add {currently_selected_medication_name} Instance for '
                                          f'{self.resident_selection_details}', geometry='600x525',
                previous_window=self.window, resident_medication_window=self,
                selected_medication_id=self.selected_medication_id)
            add_medication_instance_window.center_window(600, 525)

        else:
            WindowManager.make_message_box(title='Error',
                                           message=f'Please select a medication before trying to add an instance.',
                                           icon='error')

    def show_add_medication_instance_dose_window(self):
        if self.selected_medication_info_id:

            self.window.withdraw()

            add_medication_instance_dose_window = AddMedicationInstanceDoseWindow(
                master=self.window,
                title=f'Add {self.last_selected_medication_name} Instance Dose For {self.resident_selection_details}',
                geometry='600x400', previous_window=self.window,
                selected_medication_info_id=self.selected_medication_info_id, resident_medication_window=self)
            add_medication_instance_dose_window.center_window(600, 400)

        else:
            WindowManager.make_message_box(title='Error',
                                           message=f'Please select a medication instance before trying to add a dose.',
                                           icon='error')

    # CREATE EXPIRY DATE PDF REPORT
    def create_expiry_date_pdf_report(self):
        expiry_dates = (DatabaseManager.collect_medications_instances_expiry_dates(DatabaseManager(),
                                                                                   self.resident_selection_id))
        expired = []
        expired_medication_names = []

        due_to_expire = []
        due_to_expire_medication_names = []

        in_date = []
        in_date_medication_names = []

        no_expiry_date = []
        no_expiry_date_medication_names = []

        for date in expiry_dates:
            matched_medication_id = DatabaseManager.collect_medication_ids_where_dates_match(DatabaseManager(),
                                                                                             date=date)[0][0]
            matched_medication_name = DatabaseManager.collect_medication_name(DatabaseManager(),
                                                                              medication_id=matched_medication_id)[0][0]
            try:
                date_time_obj = datetime.strptime(date, '%m/%d/%y').date()
                day_difference = (date_time_obj - datetime.now().date()).days

                if day_difference < 0:
                    expired.append(date_time_obj)
                    expired_medication_names.append(matched_medication_name)

                elif day_difference <= 30:
                    due_to_expire.append(date_time_obj)
                    due_to_expire_medication_names.append(matched_medication_name)

                else:
                    in_date.append(date_time_obj)
                    in_date_medication_names.append(matched_medication_name)

            except ValueError:
                no_expiry_date.append(date)
                no_expiry_date_medication_names.append(matched_medication_name)

        # GENERATE EXPIRY PDF REPORT
        report_owner_and_time = f'{self.resident_selection_details.split()[0]} '\
            f'{self.resident_selection_details.split()[1]} '\
            f'{self.resident_selection_details.split()[3].replace("/", "-")} '\
            f'{datetime.now().strftime("%m-%d-%Y, %H-%M-%S")}'

        pdf = fpdf.FPDF(format='letter')
        pdf.set_font("Courier", size=8)

        def add_page(values, text):
            pdf.add_page()
            pdf.write(5, report_owner_and_time)
            pdf.ln()
            pdf.write(5, text)
            pdf.ln()
            for medication_name in values:
                pdf.write(5, medication_name)
                pdf.ln()

        # EXPIRED ITEMS PAGE
        add_page(expired_medication_names, f'{len(expired)} Expired Items:')

        # ITEMS EXPIRING WITHIN 30 DAYS PAGE
        add_page(due_to_expire_medication_names, f'{len(due_to_expire)} Items Expiring Within 30 Days:')

        # ITEMS IN DATE PAGE
        add_page(in_date_medication_names, f'{len(in_date)} Items In-Date:')

        # ITEMS WITHOUT AN EXPIRY DATE PAGE
        add_page(no_expiry_date_medication_names, f'{len(no_expiry_date)} Items Without an Expiry Date:')

        pdf.output(f'Reports/Expiry Report for {report_owner_and_time}.pdf ')

        WindowManager.make_message_box(
            title='Success', message=f'Expiry Date Report Created.', icon='info')

    # MODIFY INSTANCE STOCK LEVEL
    def modify_instance_stock_level(self):
        if self.selected_medication_info_id:
            try:
                float(self.modify_medication_instance_stock_field.get())

                DatabaseManager.modify_medication_instance_quantity(
                    self=DatabaseManager(), modify_stock_field=self.modify_medication_instance_stock_field.get(),
                    medication_info_id=self.selected_medication_info_id)

                self.populate_medication_instance_listbox()
                self.medication_instance_selection_listbox.selection_set(
                    first=self.last_selected_medication_instance_index)
                self.populate_medication_instance_dose_listbox()

                self.modify_medication_instance_stock_field.delete(0, 'end')

                WindowManager.make_message_box(
                    title='Success', message=f'{self.last_selected_medication_name} quantity updated.', icon='info')

            except ValueError:
                WindowManager.make_message_box(title="Error", message='Please enter a number and try again.',
                                               icon='error')
        else:
            WindowManager.make_message_box(
                title="Error", message='Please select a medication instance before trying to modify stock level.',
                icon='error')

    # SHOW MEDICATION NOTES WINDOW
    def show_medication_notes_window(self):
        if self.medication_notes_window_open is True:

            WindowManager.make_message_box(title='Error',
                                           message=f'Please close the current notes window and try again..',
                                           icon='error')

        elif self.selected_medication_id == '':

            WindowManager.make_message_box(title='Error',
                                           message=f'Please select a medication before trying to view notes.',
                                           icon='error')

        else:
            medication_notes_window = MedicationNotesWindow(master=self.window, geometry='600x400',
                                                            title=f'Medication Notes For '
                                                                  f'{self.last_selected_medication_name} '
                                                                  f'Owned By {self.resident_selection_details}',
                                                            selected_medication_id=self.selected_medication_id,
                                                            previous_window=self.window,
                                                            resident_medication_window=self)
            medication_notes_window.center_window(600, 400)

            self.medication_notes_window_open = True

    # LOOKUP MEDICATION
    def lookup_medication(self):
        if self.selected_medication_id:
            WindowManager.make_message_box(
                title='Success', message=f'Looking up {self.last_selected_medication_name}.', icon='info')

            medicine_repository = 'https://www.medicines.org.uk/emc/search?q='

            webbrowser.open(medicine_repository + self.last_selected_medication_name)

        else:
            WindowManager.make_message_box(
                title="Error", message='Please select a medication before trying to use the lookup feature.',
                icon='error')

    # GET LAST SELECTED MEDICATION NAME
    def get_last_selected_medication_name(self):
        self.last_selected_medication_name = DatabaseManager.collect_medication_name(
            DatabaseManager(), self.selected_medication_id)[0][0]

    # SET self.medication_notes_window_open TO FALSE
    def set_medication_notes_window_open_to_false(self):
        self.medication_notes_window_open = False

    # POPULATE MEDICATION LISTBOX
    def populate_medication_listbox(self):
        self.medication_selection_listbox.delete(first=0, last=tk.END)

        collected_medication = DatabaseManager().collect_resident_medication(resident_id=self.resident_selection_id)

        self.medication_ids = []

        for i, medication in enumerate(collected_medication):
            medication_id = medication[0]
            medication_name = medication[1]
            medication_other_name = medication[2]

            self.medication_selection_listbox.insert(i, f'{medication_name} - {medication_other_name}')
            self.medication_ids.append(medication_id)

    # POPULATE MEDICATION INSTANCE LISTBOX
    def populate_medication_instance_listbox(self):
        self.medication_instance_selection_listbox.delete(first=0, last=tk.END)

        collected_medication_instances = DatabaseManager().collect_medication_instances(
            medication_id=self.last_selected_medication_id)

        self.medication_info_ids = []

        for i, medication_instance in enumerate(collected_medication_instances):
            instance_id = medication_instance[0]
            instance_expiry = medication_instance[1]
            instance_quantity = medication_instance[2]
            instance_strength = medication_instance[3]
            instance_type = medication_instance[4]
            # instance_notes = medication_instance[5]
            # instance_medication_id = medication_instance[6]
            instance_supplier = medication_instance[7]
            instance_measurement = medication_instance[8]

            self.medication_instance_selection_listbox.insert(i, f'{str(i + 1)}: - Expiry: {instance_expiry} - '
                                                                 f'Quantity: {str(instance_quantity)} '
                                                                 f'{instance_type} - Strength: '
                                                                 f'{str(instance_strength)}{instance_measurement} - '
                                                                 f'Supplier: {instance_supplier}')

            self.medication_info_ids.append(instance_id)

    # POPULATE MEDICATION INSTANCE DOSE LISTBOX
    def populate_medication_instance_dose_listbox(self):
        current_strength = DatabaseManager().collect_quantity_and_strength(self.last_selected_medication_info_id)[0]
        current_quantity = DatabaseManager().collect_quantity_and_strength(self.last_selected_medication_info_id)[1]

        self.medication_instance_dose_selection_listbox.delete(first=0, last=tk.END)

        collected_medication_instance_doses = DatabaseManager().collect_medication_instance_doses(
            medication_info_id=self.last_selected_medication_info_id)

        for i, medication_instance_dose_info in enumerate(collected_medication_instance_doses):
            # dose_info_id = medication_instance_dose_info[0]
            dose_info_dose = medication_instance_dose_info[1]
            dose_info_measurement = medication_instance_dose_info[2]
            dose_info_frequency_per_day = medication_instance_dose_info[3]
            dose_info_regular_or_prn = medication_instance_dose_info[4]

            # CALCULATES HOW MANY DAYS WORTH OF A MEDICATION INSTANCE REMAINS AT DOSE SELECTED
            if dose_info_regular_or_prn != 'PRN' and dose_info_frequency_per_day != 0:
                how_many_days_remaining = round((current_strength * current_quantity) /
                                                (dose_info_dose * dose_info_frequency_per_day), 2)
            else:
                how_many_days_remaining = 'N/A'

            self.medication_instance_dose_selection_listbox.insert(i, f'{str(i + 1)}: - Dose: {str(dose_info_dose)}'
                                                                      f'{dose_info_measurement} - Frequency Per Day: '
                                                                      f'{str(dose_info_frequency_per_day)} - '
                                                                      f'Regularity: {dose_info_regular_or_prn} '
                                                                      f'- Days Remaining: '
                                                                      f'{str(how_many_days_remaining)}')

    # CLEAR MEDICATION LIST BOX
    def clear_medication_listbox(self):
        self.medication_selection_listbox.delete(first=0, last=tk.END)

    # CLEAR MEDICATION INSTANCES LIST BOX
    def clear_medication_instances_listbox(self):
        self.medication_instance_selection_listbox.delete(first=0, last=tk.END)

    # CLEAR MEDICATION INSTANCE DOSES LIST BOX
    def clear_medication_instance_doses_listbox(self):
        self.medication_instance_dose_selection_listbox.delete(first=0, last=tk.END)

    # CLEAR LIST BOXES
    def clear_boxes(self):
        self.medication_selection_listbox.delete(first=0, last=tk.END)
        self.medication_instance_selection_listbox.delete(first=0, last=tk.END)
        self.medication_instance_dose_selection_listbox.delete(first=0, last=tk.END)


class AddMedicationWindow(WindowManager):
    def __init__(self, master, title, geometry, previous_window, selected_resident_id, resident_medication_window):
        super().__init__(master, title, geometry, previous_window)

        self.selected_resident_id = selected_resident_id
        self.resident_medication_window = resident_medication_window

        # WIDGETS
        # LABELS AND ENTRY FIELDS
        WindowManager.make_label(self, text='Name', pad_x=0, pad_y=0)
        self.medication_name_field = WindowManager.make_entry_field(self)

        WindowManager.make_label(self, text='Other Name', pad_x=0, pad_y=0)
        self.medication_other_name_field = WindowManager.make_entry_field(self)

        WindowManager.make_button(self, text='Add', command=self.add_medication_to_database, state='active', pad_x=0,
                                  pad_y=5, side=tk.TOP)

    # BUTTON COMMANDS
    def add_medication_to_database(self):
        if self.medication_name_field.get().isalpha() and self.medication_other_name_field.get().isalpha():
            DatabaseManager.add_medication_to_database(self=DatabaseManager(),
                                                       medication_name=self.medication_name_field.get(),
                                                       medication_other_name=self.medication_other_name_field.get(),
                                                       resident_id=self.selected_resident_id)
            self.window.destroy()
            self.previous_window.deiconify()
            ResidentMedicationWindow.clear_boxes(self=self.resident_medication_window)
            ResidentMedicationWindow.populate_medication_listbox(self=self.resident_medication_window)
            WindowManager.make_message_box(title='Success', message='Medication added to database.', icon='info')
        else:
            WindowManager.make_message_box(title="Error", message='Please fill in all fields correctly and try again.',
                                           icon='error')


class AddMedicationInstanceWindow(WindowManager):
    def __init__(self, master, title, geometry, previous_window, resident_medication_window, selected_medication_id):
        super().__init__(master, title, geometry, previous_window)

        self.resident_medication_window = resident_medication_window
        self.selected_medication_id = selected_medication_id

        # WIDGETS
        # LABELS, SCALES, COMBO BOXES AND BUTTON
        WindowManager.make_label(self, text='Quantity', pad_x=0, pad_y=0)
        self.quantity_scale = WindowManager.make_scale(self)

        WindowManager.make_label(self, text='Strength', pad_x=0, pad_y=0)
        self.strength_scale = WindowManager.make_scale(self)

        WindowManager.make_label(self, text='Measurement', pad_x=0, pad_y=0)
        measurement_list_items = ['', 'g', 'mg', 'mcg']
        self.measurement_combo_box = WindowManager.make_combo_box(self, list_items=measurement_list_items)

        WindowManager.make_label(self, text='Form', pad_x=0, pad_y=0)
        form_list_items = sorted(['', 'Tablets', 'Caplets', 'Capsules', 'Effervescent Tablets', 'Roll', 'Dressing',
                                  'Liquid (ml)', 'Sachets'])
        self.form_combo_box = WindowManager.make_combo_box(self, list_items=form_list_items)

        WindowManager.make_label(self, text='Supplier', pad_x=0, pad_y=0)
        self.supplier_entry_field = WindowManager.make_entry_field(self)

        WindowManager.make_label(self, text='Select Expiry Date', pad_x=0, pad_y=5)
        self.expiry_date_picker = WindowManager.make_date_picker(self, start_year=2021)

        self.add_medication_instance_button = WindowManager.make_button(
            self, text='Add Instance', command=self.add_medication_instance_to_database, side=tk.TOP, state='active',
            pad_x=0, pad_y=5)

# BUTTON COMMANDS
    def add_medication_instance_to_database(self):
        DatabaseManager.add_medication_instance_to_database(self=DatabaseManager(),
                                                            instance_expiry=self.expiry_date_picker.get_date(),
                                                            instance_measurement=self.measurement_combo_box.get(),
                                                            instance_medication_id=self.selected_medication_id,
                                                            instance_medication_type=self.form_combo_box.get(),
                                                            instance_quantity=self.quantity_scale.get(),
                                                            instance_strength=self.strength_scale.get(),
                                                            instance_supplier=self.supplier_entry_field.get())
        self.window.destroy()
        self.previous_window.deiconify()

        ResidentMedicationWindow.populate_medication_instance_listbox(self.resident_medication_window)
        ResidentMedicationWindow.clear_medication_instance_doses_listbox(self.resident_medication_window)

        WindowManager.make_message_box(title='Success', message='Medication instance added to database.', icon='info')


class AddMedicationInstanceDoseWindow(WindowManager):
    def __init__(self, master, title, geometry, previous_window, resident_medication_window,
                 selected_medication_info_id):
        super().__init__(master, title, geometry, previous_window)

        self.resident_medication_window = resident_medication_window
        self.selected_medication_info_id = selected_medication_info_id

# WIDGETS
# LABELS, SCALES, COMBO BOXES, AND BUTTON
        WindowManager.make_label(self, text='Dose', pad_x=0, pad_y=0)
        self.dose_scale = WindowManager.make_scale(self)

        WindowManager.make_label(self, text='Measurement', pad_x=0, pad_y=0)
        measurement_list_items = ['', 'g', 'mg', 'mcg']
        self.measurement_combobox = WindowManager.make_combo_box(self, list_items=measurement_list_items)

        WindowManager.make_label(self, text='Frequency Per Day', pad_x=0, pad_y=0)
        frequency_per_day_list_items = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        self.frequency_per_day_combobox = WindowManager.make_combo_box(self, list_items=frequency_per_day_list_items)
        self.frequency_per_day_combobox.set('0')

        WindowManager.make_label(self, text='Regularity', pad_x=0, pad_y=0)
        self.regularity_combobox_list_items = sorted(['Regular', 'PRN'])
        self.regularity_combobox = WindowManager.make_combo_box(self, list_items=self.regularity_combobox_list_items)

        self.add_dose_button = WindowManager.make_button(self, text='Add',
                                                         command=self.add_medication_instance_dose_to_database,
                                                         state='active', side=tk.TOP, pad_x=0, pad_y=5)

# BUTTON COMMANDS
    def add_medication_instance_dose_to_database(self):
        DatabaseManager.add_medication_instance_dose_to_database(self=DatabaseManager(),
                                                                 dose_amount=self.dose_scale.get(),
                                                                 dose_frequency=self.frequency_per_day_combobox.get(),
                                                                 dose_measurement=self.measurement_combobox.get(),
                                                                 dose_medication_info_id=self.
                                                                 selected_medication_info_id,
                                                                 dose_regularity=self.regularity_combobox.get())
        self.window.destroy()
        self.previous_window.deiconify()

        ResidentMedicationWindow.populate_medication_instance_dose_listbox(self.resident_medication_window)
        WindowManager.make_message_box(title='Success', message='Medication instance dose added to database.',
                                       icon='info')


class MedicationNotesWindow(WindowManager):
    def __init__(self, master, title, geometry, previous_window, selected_medication_id, resident_medication_window):
        super().__init__(master, title, geometry, previous_window)

        self.selected_medication_id = selected_medication_id
        self.resident_medication_window = resident_medication_window

        self.window.protocol('WM_DELETE_WINDOW', self.on_exit)

# WIDGETS
# TEXT BOX AND BUTTON
        self.medication_notes_text_box = WindowManager.make_text_box(self, width=70, height=22)
        self.populate_medication_notes_text_box()

        WindowManager.make_button(self, text='Save Notes', command=self.add_medication_notes_to_database,
                                  state='active', side=tk.TOP, pad_x=0, pad_y=5)

# ON THIS WINDOW EXIT
    def on_exit(self):
        ResidentMedicationWindow.set_medication_notes_window_open_to_false(self.resident_medication_window)
        self.window.destroy()

# BUTTON COMMANDS
    def add_medication_notes_to_database(self):
        DatabaseManager.add_medication_notes_to_database(
            self=DatabaseManager(), notes_text_box=self.medication_notes_text_box.get('1.0', 'end'),
            medication_id=self.selected_medication_id)
        self.on_exit()
        WindowManager.make_message_box(title='Success', message='Notes successfully updated.', icon='info')

# POPULATE MEDICATION NOTES TEXTBOX
    def populate_medication_notes_text_box(self):
        self.medication_notes_text_box.delete(1.0, "end")
        self.medication_notes_text_box.insert("end", DatabaseManager.
                                              collect_medication_notes(DatabaseManager(),
                                                                       medication_id=self.selected_medication_id))


# MAIN LOOP
def main():
    database = DatabaseManager()
    database.create_tables()

    root = tk.Tk()
    root.iconbitmap(r'icon.ico')
    root.withdraw()

    primary_window = PrimaryWindow(master=root, title='Nurse Aid', geometry='220x70', previous_window=root)
    primary_window.center_window(x=220, y=70)

    root.mainloop()

    database.connection.close()


if __name__ == '__main__':
    main()

# TODO Low remaining days worth alert
# TODO Expiry date traffic light system
# TODO Dose administration system
