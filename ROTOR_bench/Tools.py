#
# Copyright 2024 Jean-Luc.CHARLES@mailo.com
#
    
def get_RotStep():
    while True:
        question = f"Rotation step (must be a multiple of 1.2°) ? "
        rot_step = get_param_from_user(question, float, 1.2, 120, True)

        if 10*rot_step % 12 != 0:
            print(f"the rotation step {rot_step}, {type(rot_step)} is not a multiple of 1.2° !")
            continue
        else:
            NBSTEP1 = round(rot_step*RATIO1/STEPPER_ANGLE1)
            break
        
    return rot_step, NBSTEP1

def get_ZPOS():

    Zpos_mm = []
    while True:
      question = f"# of vertical positions for the sensor in range [{MIN_NB_ZPOS}, {MAX_NB_ZPOS}] ? "
      nb_sensor_pos = get_param_from_user(question, int, MIN_NB_ZPOS, MAX_NB_ZPOS, False)

      for n in range(1, nb_sensor_pos+1):
        question = F"position #{n} from top in mm ? "
        z_mm = get_param_from_user(question, int, ZPOS_MIN, ZPOS_MAX, False)
        Zpos_mm.append(z_mm)

      print("\nPositions along Z (from top):")
      
      for n in range(1, nb_sensor_pos+1):
        print(f"   pos #{n}: {Zpos_mm[n]:03d} mm")
        
      rep = input("Do you confirm these values ? y/n ?")
      if rep.lower() == 'y':
        break

    return Zpos_mm
    
def get_param_from_user(mess:str,
                        data_type,
                        min_value:int,
                        max_value:int,
                        confirm:bool):
    '''
    To get value for some usefull parameters.
    The value must be in the range [min_value, max_value].
    If confirm is True, a confirmation yes/no about the value is proposed
    '''
    while True:
        value = input(mess)
        try:
            value = data_type(value)
        except:
            print("Incorrect value... please type in a new value")
            continue
        else:
            if value < min_value or value > max_value:
                print('value must be in [{min_value}, {max_value}]')
                continue
        if confirm:
            rep = input(f'You typed <{value}>, confirm: [y]/n ? ')
            if rep.lower() == 'y': break
        else:
            break
    return value

def uniq_file_name_ROTOR(now, work_dist, rot_step, Zpos_mm, repet, mode):
    '''
    Defines a uniq file name mixing date info and parameters info.
    '''
    fileName = f'TXT/ROTOR_{now.strftime("%Y-%m-%d-%H-%M")}'
    fileName += f'_WDIST-{work_dist}'
    fileName += f'_ROTSTEP-{rot_step:.1f}'
    for z in Zpos_mm:
        fileName += f'_{z:03d}'
    n,m = repet
    fileName+= f"_{n}of{m}"
    fileName += '.txt'
    
    return fileName

def uniq_file_name_FREE(now, duration, sampling, SAMPLE=None, GAIN=None, DELAY=None, repet=(1,1)):
    '''
    Defines a uniq file name mixing date info and parameters info.
    '''
    fileName = f'TXT/FREE_{now.strftime("%Y-%m-%d-%H-%M")}'
    if SAMPLE is None: SAMPLE = Params['SENSOR_NB_SAMPLE']
    if GAIN is None: GAIN =  Params['SENSOR_GAIN']
    if DELAY is None: DELAY = Params['SENSOR_READ_DELAY']
    fileName += f'_SMPL-{SAMPLE:03d}'
    fileName += f'_GAIN-{GAIN:02d}'
    fileName += f'_DELAY-{DELAY:04.2f}'
    n,m = repet
    fileName+= f"_{n}of{m}"
    fileName += '.txt'
    
    return fileName

def touch_txt_by_date():
    '''
    To touch files *.txt in TXT dir so as to use the date included in the filenames...
    '''
    
    import os
    from pathlib import Path
    import calendar, time
    
    working_dir = Path(os.getcwd())
    print(f'Working dir: {working_dir}')
    
    TXT_dir = Path(working_dir) / 'TXT'
    os.chdir(TXT_dir)
    
    working_dir = Path(os.getcwd())
    print(f'Working dir: {working_dir}')
    
    list_txt = [f for f in os.listdir(working_dir) if f.endswith("txt")]
    
    for f in list_txt:
        f_path = Path(working_dir, f)
        date = f.split('_')[1]
        print(f'Processing file <{f}> with date <{date}>')

        m_epoch = calendar.timegm(time.strptime(f'{date}', '%Y-%m-%d-%H-%M'))
        m_epoch -= 3600
        if "2024-03-03-02-00" < date < "2024-10-27-03-00": m_epoch -=3600
        
        os.utime(f_path, (m_epoch, m_epoch))
        
    
