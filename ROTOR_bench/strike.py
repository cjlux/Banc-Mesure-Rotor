import sys, os, json
from ROTOR_bench import ROTOR_bench
from ROTOR_config import StepperMotor

Stepper1 = StepperMotor("Stepper motor connected to the shaft",
                        STEP_MODE=1, STEPPER_ANGLE=1.8, NB_STEP_PER_REVOL=200,
                        NB_REVOL_PER_SEC=0.5,
                        GPIO_DIR=17, GPIO_STEP=27, GPIO_ENA=22,
                        RATIO=6)

Stepper2 = StepperMotor("Stepper motor for the sensorZ motion", 
                        STEP_MODE=1, STEPPER_ANGLE=1.8, NB_STEP_PER_REVOL=200,
                        NB_REVOL_PER_SEC=0.5,
                        GPIO_DIR=10, GPIO_STEP=9, GPIO_ENA=11,
                        RATIO=None,
                        DIAM_MM=10)

R = ROTOR_bench(Stepper1, Stepper2)
paramFile = "/tmp/ROTOR_LAUNCH.txt"

if (os.path.exists(paramFile)):
    with open(paramFile, "r", encoding="utf8") as f:
        params = json.loads(f.read())
    print("params:", params)
    os.remove(paramFile)
    print(f"Found file <{paramFile}>, using params: {params}")

else:
    # If file /tmp/ROTOR_LAUNCH.txt is not found use these parameters:
    params = {'MODE': 'RunBench',
              'WORK_DIST': 12,
              'ROT_STEP_DEG': 4.8,
              'Z_POS_MM':[0, 30, 60, 90],
              'NB_REPET': 1}
    print(f"File <{paramFile}> not found... using params:<{params}>")

if params['MODE'] == 'RunBench':
    R.run(params, verbose=True)
    
elif params['MODE'] == 'RunFree':
    R.run_free(params)
    
elif params['MODE'] == 'ReleaseMotors':
    R.Stop_ROTOR_Bench()
    

