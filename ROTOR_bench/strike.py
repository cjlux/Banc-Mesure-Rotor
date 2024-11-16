import sys, os, json
from ROTOR_bench import ROTOR_bench
from ROTOR_config import StepperMotor

#
# This is the file that is in charge :
#  1/ To define the properties of the 2 stepper motors of the measurement bench
#  2/ to instanciate a ROTOR_bench object, passing the 2 stepper motors as arguments
#  3/ To read the  paramFile (/tmp/ROTOR_LAUNCH.txt) and to lauch the right ROTOR_bench
#     method depending on the value of MODE in the paramfile.
#      
Stepper1 = StepperMotor("Stepper motor connected to the shaft",
                        STEP_MODE=1, STEPPER_ANGLE=1.8, NB_STEP_PER_REVOL=200,
                        NB_REVOL_PER_SEC=0.3,
                        GPIO_DIR=17, GPIO_STEP=27, GPIO_ENA=22,
                        RATIO=6)

Stepper2 = StepperMotor("Stepper motor for the sensorZ motion", 
                        STEP_MODE=1, STEPPER_ANGLE=1.8, NB_STEP_PER_REVOL=200,
                        NB_REVOL_PER_SEC=0.5,
                        GPIO_DIR=10, GPIO_STEP=9, GPIO_ENA=11,
                        RATIO=None,
                        DIAM_MM=10)

paramFile = "/tmp/ROTOR_LAUNCH.txt"

if (os.path.exists(paramFile)):
    with open(paramFile, "r", encoding="utf8") as f:
        params = json.loads(f.read())
    print("params:", params)
    os.remove(paramFile)
    print(f"Found file <{paramFile}>, using params: {params}")

else:
    # If file /tmp/ROTOR_LAUNCH.txt is not found use these parameters:
    params = {'MODE': 'ByAngle',
              'WORK_DIST': 12,
              'ROT_STEP_DEG': 120,
              'Z_POS_MM':[30],
              'NB_REPET': 1}
    print(f"File <{paramFile}> not found... using params:<{params}>")

match(params['MODE']):
    
    case 'ByZPos':
        R = ROTOR_bench(Stepper1, Stepper2)
        R.run_by_ZPos(params, verbose=True)
    
    case 'ByAngle':
        R = ROTOR_bench(Stepper1, Stepper2)
        R.run_by_Angle(params, verbose=True)

    case 'Free':
        R = ROTOR_bench(Stepper1, Stepper2)
        R.run_free(params)
    
    case 'ReleaseMotors':
        R = ROTOR_bench(Stepper1, Stepper2, init_serial=False)
        R.Stop_ROTOR_Bench()
    

