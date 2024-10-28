#Steps to add a UI into the application (Application Structure)
#import modules
#class definition and implementation (GUI CLASS)
#object Show (Objects of each class in the application)
"""
import sys
from PyQt5.QtWidgets import QApplication, QWidget

#widget: is refer to the all of the graphical shapes in our application and each of them has a group behaviour like "push button" widget.

class F(QWidget):
    def __init__(self, ) -> None:
        super().__init__()
        self.setUI()
    
    def setUI(self,):
        self.setGeometry(80,80,300,300) #position of starting point for the location from top-left - and dimention
        self.setWindowTitle("Differential Diflection Method")
        self.show()
    




if __name__ == "__main__":
    print(__name__)
    app = QApplication(sys.argv)
    ex = F()
    sys.exit(app.exec_())
"""