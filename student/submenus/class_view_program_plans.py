import os
import sys

from PyQt6.QtWidgets import (
    QWidget,
    QApplication,
    QTableWidgetItem,
    QMessageBox,
)
from PyQt6.QtCore import Qt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app_ui.student_ui.submenus_ui.ui_view_program_plans import Ui_ViewProgramPlans
from admin.class_admin_utilities import admin
from helper_files.shared_utilities import BaseLoginForm, warning, info, error

class ViewProgramPlansWidget(QWidget):
    def __init__(self, admin_utils, parent=None):
        super().__init__(parent)
        self.ui = Ui_ViewProgramPlans()
        self.ui.setupUi(self)
        self.blf = BaseLoginForm()

        self.admin_utils = admin_utils
        self.all_rows = []  # (program, code, name, credits, level)

        self.setup_programs_combo()
        self.setup_levels_combo()

        # ربط الأزرار
        self.ui.buttonRefresh.clicked.connect(self.load_plans)
        self.ui.comboBoxSelectProgram.currentIndexChanged.connect(self.load_plans)
        self.ui.comboBoxLevel.currentIndexChanged.connect(self.load_plans)


        table = self.ui.tableAllCourses
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setSelectionMode(table.SelectionMode.MultiSelection)
        table.setEditTriggers(table.EditTrigger.NoEditTriggers)

    

        # ما نحمّل شيء في البداية إلى أن يختار برنامج
        self.fill_table([])

    # ----------------- إعداد الكمبوبوكس -----------------

    def setup_programs_combo(self):
        cb = self.ui.comboBoxSelectProgram
        cb.clear()
        cb.addItem("Select program...", None)  # ما في بيانات إلا بعد الاختيار

        programs = [
            ("PWM",  "Power & Machines Engineering"),
            ("BIO",  "Biomedical Engineering"),
            ("COMM", "Communications Engineering"),
            ("COMP", "Computer Engineering"),
        ]
        for code, label in programs:
            cb.addItem(f"{code} - {label}", code)

    def setup_levels_combo(self):
        cb = self.ui.comboBoxLevel
        cb.clear()
        cb.addItem("All Levels", None)
        for lvl in range(1, 9):
            cb.addItem(f"Level {lvl}", lvl)

    # ----------------- تحميل وفلترة وترتيب -----------------

    def load_plans(self):
        program_code = self.ui.comboBoxSelectProgram.currentData()

        # ما نعرض شيء إذا ما اختار برنامج
        if program_code is None:
            self.all_rows = []
            self.fill_table([])
            return

        # نجيب مواد الخطة لهذا البرنامج فقط
        rows = self.admin_utils.db.list_plan_courses(program=program_code)
        self.all_rows = rows

        level_filter = self.ui.comboBoxLevel.currentData()

        if level_filter is not None:
            rows = [r for r in rows if r[4] == level_filter]  # r[4] = level

        # ترتيب حسب الـ level
        rows.sort(key=lambda r: r[4])

        self.fill_table(rows)

    def fill_table(self, rows):
        table = self.ui.tableAllCourses
        table.setRowCount(len(rows))

        for i, (program, code, name, credits, level) in enumerate(rows):
            # #
            item0 = QTableWidgetItem(str(i + 1))
            item0.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 0, item0)

            # LEVEL
            item1 = QTableWidgetItem(str(level))
            item1.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 1, item1)

            # COURSE CODE (نخزن البرنامج في الـ UserRole)
            item2 = QTableWidgetItem(code)
            item2.setData(Qt.ItemDataRole.UserRole, program)
            item2.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 2, item2)

            # COURSE NAME
            item3 = QTableWidgetItem(name)
            item3.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 3, item3)

            # CREDIT HOURS
            item4 = QTableWidgetItem(str(credits))
            item4.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 4, item4)

            # PREREQUISITES (فاضي حالياً)
            item5 = QTableWidgetItem("")
            item5.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 5, item5)

            # ACTION (فاضي)
            item6 = QTableWidgetItem("")
            item6.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 6, item6)





if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ViewProgramPlansWidget(admin)
    w.show()
    sys.exit(app.exec())