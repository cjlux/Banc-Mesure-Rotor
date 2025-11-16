#
# Copyright 2024-2025 Jean-Luc.CHARLES@mailo.com
#

from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QApplication
from PyQt5.QtCore import Qt
        
class FastStepSpinBox(QSpinBox):
    '''
    A subclass of QSpinbox that allows fast stepping when Shift is held.
    '''
    
    clic_shiftclick = 'Use click/mouse_wheel or Shift+ click/mouse_wheel to change faster.' 
        
    def __init__(self, default_step, fast_step, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_step = default_step
        self.fast_step    = fast_step
        self.setSingleStep(self.default_step)
        self._fast_mode   = False

    def setFastStep(self, step):
        self.fast_step = step

    def stepBy(self, steps):
        modifiers = QApplication.keyboardModifiers()
        # Use fast step if Shift is held, otherwise default
        step = self.fast_step if modifiers & Qt.ShiftModifier else self.default_step
        self.setSingleStep(step)
        super().stepBy(steps)

class FastStepDoubleSpinBox(QDoubleSpinBox):
    '''
    A subclass of QDoubleSpinBox that allows fast stepping when Shift is held.
    '''
    
    clic_shiftclick = 'Use click/mouse_wheel or Shift+ click/mouse_wheel to change faster.' 
        
    def __init__(self, default_step, fast_step, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_step = default_step
        self.fast_step    = fast_step
        self.setSingleStep(self.default_step)
        self._fast_mode   = False
        
    def setFastStep(self, step):
        self.fast_step = step

    def stepBy(self, steps):
        modifiers = QApplication.keyboardModifiers()
        # Use fast step if Shift is held, otherwise default
        step = self.fast_step if modifiers & Qt.ShiftModifier else self.default_step
        self.setSingleStep(step)
        super().stepBy(steps)
