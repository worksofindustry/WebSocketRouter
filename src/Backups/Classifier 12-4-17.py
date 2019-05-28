import numpy as np
import scipy
from sklearn.metrics import mean_squared_error
from math import sqrt
import pandas as pd
import glob

class Classifier:
    
    def __init__(self, windowsize):
        
        self.__VOTING = 'DEMOCRACY' # AUTOCRACY or DEMOCRACY
        self.__WINDOWSIZE = windowsize
        
        # agricultural
        self.__CENTROID_IDLE_AG = [9.81048074, 357.2467782, 0.164081334, 9.811358838, 357.2467782, 0.162985725, 9.843733014, 357.2467782, 0.211950122, 9.782932775, 357.2467782, 0.126240411, 0.011856885, 2.07393E-11, 0.023294993, 2309.902326, 3063006.253, 0.658240896]
        self.__CENTROID_DIGGING_AG = [9.897395248, 197.9406194, 1.84999849, 9.895659054, 197.6482603, 1.67741165, 10.12797667, 274.1141176, 2.986290483, 9.673458946, 120.4181023, 1.158705389, 0.112820484, 48.58390334, 0.445837039, 2351.609307, 1025303.097, 92.79783377]
        
        # excavator
        self.__CENTROID_IDLE_EX = [9.592430956,210.4580805,2.511377694,9.596267677,215.2723905,2.48760376,9.730717817,248.8420751,3.189236649,9.448609731,137.4235406,1.735162609,0.054777954,23.12843838,0.35806633,2208.725466,1126626.148,159.5876863]
        self.__CENTROID_DRIVING_EX = [9.941491098,189.3728933,12.77598823,9.827602396,193.1653681,11.87425684,10.87718729,269.75025,25.52027592,9.38725472,106.1026312,4.579023745,0.384106937,44.09244904,5.284652645,2377.52571,908873.0429,5013.388084]
        self.__CENTROID_DIGGING_EX = [9.662783462,194.7784556,9.961569832,9.649406563,197.3283117,9.164325543,10.00889329,261.0325514,17.78090089,9.345941801,138.1069011,4.425731521,0.156357119,29.30385507,3.590932103,2241.502017,962900.2921,2799.827016]
        
        # backhoe
        self.__CENTROID_IDLE_BH = [9.690071485, 122.1047681, 0.200719267, 9.690830252, 122.0990377, 0.195333662, 9.754620079, 150.2325583, 0.26237892, 9.634666848, 122.0297089, 0.143863011, 0.010278958, 0.059012267, 0.032891951, 2253.598003, 373967.6249, 1.002102832]
        self.__CENTROID_DRIVING_BH = [9.710696694,164.4427455,2.263824,9.692516808,158.80848,2.088083181,10.00602103,270.8428437,4.084220692,9.445359162,84.1623262,1.036258666,0.154202474,50.45999453,0.80975704,2264.034974,728161.6463,144.6831279]
        self.__CENTROID_DIGGING_BH = [9.604662112,219.2339144,0.543725981,9.604937145,219.5929495,0.485779303,9.84783354,226.2126479,0.95245086,9.381238456,213.1616652,0.277303457,0.11742647,0.501343103,0.169840706,2214.450737,1159766.232,8.179674273]
        
    # 7-point smoothing
    def __smooth(self,d):
        #for i in range(3,len(d)-3):
        #    d[i] = (d[i-3]+d[i-2]+d[i-1]+d[i]+d[i+1]+d[i+2]+d[i+3])/7
        return d
    
    # extract feature
    def __feature(self, x):

        return np.mean(x[0:len(x)]), \
                np.median(x[0:len(x)]), \
                np.max(x[0:len(x)]), \
                np.min(x[0:len(x)]), \
                np.std(x[0:len(x)]), \
                np.sum(np.power(x[0:len(x)],2))

    # filter data
    def __filterData(self, data):

        ## filter outliers    
        outlier_indices = []

        mean = np.median(data, axis=0)
        sd = np.std(data, axis=0)

        idx = 0
        for x in data:
            if  (x <= mean - 2 * sd) or (x >= mean + 2 * sd):
                outlier_indices.append(idx)
            idx+=1

        # filtered data
        data_filtered = []

        for idx in range(len(data)):
            if idx not in outlier_indices:
                data_filtered.append(data[idx])

        # dont filter if similar data
        if not data_filtered:
            return data

        return data_filtered
    
    # get features from window
    def __getFeaturesFromWindow(self, window):
    
        # extract {accel, orient, gyro} data
        accel = []
        orient = []
        gyro = []

        for data9dof in window:
            accel.append(data9dof['accel'])
            orient.append(data9dof['orient'])
            gyro.append(data9dof['gyro'])

        # accel
        meanamp_accel, medianamp_accel, maxamp_accel, minamp_accel, stdamp_accel, energyamp_accel = self.__feature(self.__filterData(accel))
        # orient
        meanamp_orient, medianamp_orient, maxamp_orient, minamp_orient, stdamp_orient, energyamp_orient = self.__feature(self.__filterData(orient))
        # gyro
        meanamp_gyro, medianamp_gyro, maxamp_gyro, minamp_gyro, stdamp_gyro, energyamp_gyro = self.__feature(self.__filterData(gyro))

        return [meanamp_accel, medianamp_accel, maxamp_accel, minamp_accel, stdamp_accel, energyamp_accel,\
                meanamp_orient, medianamp_orient, maxamp_orient, minamp_orient, stdamp_orient, energyamp_orient,\
                meanamp_gyro, medianamp_gyro, maxamp_gyro, minamp_gyro, stdamp_gyro, energyamp_gyro]
    
    
    # excavator - clustering algorithm based on eucledian distance 
    def __ex_algorithm(self, window, deployment):

        # centroid = [mean, median, max, min, std dev, energy, energy signal]
        centroid_idle = [0.009515377, 0.000133279, 0.029404748]
        centroid_digging = [0.165121952, 0.35087555, 0.17592882]
        centroid_driving = [0.189043103,42.58465294,1.495883193]

        data_accel = []
        data_orient = []
        data_gyro = []

        for data9dof in window:
            data_accel.append(data9dof['accel'])
            data_orient.append(data9dof['orient'])
            data_gyro.append(data9dof['gyro'])

        smooth_data_accel = self.__smooth(data_accel)
        smooth_data_orient = self.__smooth(data_orient)
        smooth_data_gyro = self.__smooth(data_gyro)

        # find features
        std_accel = np.std(smooth_data_accel)
        std_orient = np.std(smooth_data_orient)
        std_gyro = np.std(smooth_data_gyro)

        # euclidean distance
        distance_idle = np.sqrt(np.square(centroid_idle[0]-std_accel) + np.square(centroid_idle[1]-std_orient) + np.square(centroid_idle[2]-std_gyro))
        distance_digging = np.sqrt(np.square(centroid_digging[0]-std_accel) + np.square(centroid_digging[1]-std_orient) + np.square(centroid_digging[2]-std_gyro))
        distance_driving = np.sqrt(np.square(centroid_driving[0]-std_accel) + np.square(centroid_driving[1]-std_orient) + np.square(centroid_driving[2]-std_gyro))

        if distance_idle<=distance_digging and distance_idle<=distance_driving:
            return 'IDLE'
        elif distance_digging<=distance_idle and distance_digging<=distance_driving:
            return 'DIGGING'
        elif distance_driving<=distance_idle and distance_driving<=distance_digging:
            return 'DRIVING'

        return 'IDLE'
    
    # algorithm -- future algorithm
    #def __ex_algorithm(self, window, deployment):
        
    #    centroid_window = self.__getFeaturesFromWindow(window)
        
    #    # option 1: one go
    #    if self.__VOTING is 'AUTOCRACY':
    #        distance_idle = sqrt(mean_squared_error(centroid_window, self.__CENTROID_IDLE_EX))
    #        distance_digging = sqrt(mean_squared_error(centroid_window, self.__CENTROID_DIGGING_EX)) 
    #        distance_driving = sqrt(mean_squared_error(centroid_window, self.__CENTROID_DRIVING_EX)) 
            
    #        # decision
    #        if distance_idle<=distance_digging and distance_idle<=distance_driving:
    #            return 'IDLE'
    #        elif distance_driving<=distance_digging and distance_driving<=distance_idle:
    #            return 'DRIVING'
    #        elif distance_digging<=distance_driving and distance_digging<=distance_idle:
    #            return 'DIGGING'

    #    ## option 2: majority voting
    #    elif self.__VOTING is 'DEMOCRACY':
    #        votes_idle = 0
    #        votes_digging = 0
    #        votes_driving = 0
            
    #        for feature_count in range(len(centroid_window)//3):
    #            fc = feature_count
    
    #            #distance_idle = sqrt(mean_squared_error(centroid_window[fc*3:(fc+1)*3-1], self.__CENTROID_IDLE_EX[fc*3:(fc+1)*3-1]))
    #            #distance_digging = sqrt(mean_squared_error(centroid_window[fc*3:(fc+1)*3-1], self.__CENTROID_DIGGING_EX[fc*3:(fc+1)*3-1])) 
    #            #distance_driving = sqrt(mean_squared_error(centroid_window[fc*3:(fc+1)*3-1], self.__CENTROID_DRIVING_EX[fc*3:(fc+1)*3-1])) 

    #            distance_idle = sqrt(mean_squared_error(centroid_window[fc*3:(fc+1)*3-1], self.__CENTROID_IDLE_EX[fc*3:(fc+1)*3-1]))
    #            distance_digging = sqrt(mean_squared_error(centroid_window[fc*3:(fc+1)*3-1], self.__CENTROID_DIGGING_EX[fc*3:(fc+1)*3-1])) 
    #            distance_driving = sqrt(mean_squared_error(centroid_window[fc*3:(fc+1)*3-1], self.__CENTROID_DRIVING_EX[fc*3:(fc+1)*3-1])) 
                
    #            # decision  
    #            if distance_idle<=distance_digging and distance_idle<=distance_driving:
    #                votes_idle += 1
    #            elif distance_driving<=distance_digging and distance_driving<=distance_idle:
    #                votes_driving += 1
    #            elif distance_digging<=distance_driving and distance_digging<=distance_idle:
    #                votes_digging += 1

    #        # vote count
    #        if votes_idle>=votes_digging and votes_idle>=votes_driving:
    #            return 'IDLE'
    #        elif votes_driving>=votes_digging and votes_driving>=votes_idle:
    #            return 'DRIVING'
    #        elif votes_digging>=votes_driving and votes_digging>=votes_idle:
    #            return 'DIGGING'
        
    #    return 'IDLE'

    # algorithm
    def __bh_algorithm(self, window, deployment):
        
        centroid_window = self.__getFeaturesFromWindow(window)
        
        # option 1: one go
        if self.__VOTING is 'AUTOCRACY':
            distance_idle = sqrt(mean_squared_error(centroid_window, self.__CENTROID_IDLE_BH))
            distance_digging = sqrt(mean_squared_error(centroid_window, self.__CENTROID_DIGGING_BH)) 
            distance_driving = sqrt(mean_squared_error(centroid_window, self.__CENTROID_DRIVING_BH)) 
            
            # decision
            if distance_idle<=distance_digging and distance_idle<=distance_driving:
                return 'IDLE'
            elif distance_driving<=distance_digging and distance_driving<=distance_idle:
                return 'DRIVING'
            elif distance_digging<=distance_driving and distance_digging<=distance_idle:
                return 'DIGGING'

        ## option 2: majority voting
        elif self.__VOTING is 'DEMOCRACY':
            votes_idle = 0
            votes_digging = 0
            votes_driving = 0

            for feature_count in range(len(centroid_window)//3):
                fc = feature_count
                    
                distance_idle = sqrt(mean_squared_error(centroid_window[fc*3:(fc+1)*3-1], self.__CENTROID_IDLE_BH[fc*3:(fc+1)*3-1]))
                distance_digging = sqrt(mean_squared_error(centroid_window[fc*3:(fc+1)*3-1], self.__CENTROID_DIGGING_BH[fc*3:(fc+1)*3-1])) 
                distance_driving = sqrt(mean_squared_error(centroid_window[fc*3:(fc+1)*3-1], self.__CENTROID_DRIVING_BH[fc*3:(fc+1)*3-1])) 

                # decision  
                if distance_idle<=distance_digging and distance_idle<=distance_driving:
                    votes_idle += 1
                elif distance_driving<=distance_digging and distance_driving<=distance_idle:
                    votes_driving += 1
                elif distance_digging<=distance_driving and distance_digging<=distance_idle:
                    votes_digging += 1

            # vote count
            if votes_idle>=votes_digging and votes_idle>=votes_driving:
                return 'IDLE'
            elif votes_driving>=votes_digging and votes_driving>=votes_idle:
                return 'DRIVING'
            elif votes_digging>=votes_driving and votes_digging>=votes_idle:
                return 'DIGGING'
        
        return 'IDLE'
    
    # algorithm
    def __ag_algorithm(self, window, deployment):
        
        centroid_window = self.__getFeaturesFromWindow(window)
        
        # option 1: one go
        if self.__VOTING is 'AUTOCRACY':
            distance_idle = sqrt(mean_squared_error(centroid_window, self.__CENTROID_IDLE_AG))
            distance_digging = sqrt(mean_squared_error(centroid_window, self.__CENTROID_DIGGING_AG)) 

            if distance_idle<=distance_digging:
                return 'IDLE-AG'
            elif distance_digging<=distance_idle:
                return 'DIGGING-AG'

        ## option 2: majority voting
        elif self.__VOTING is 'DEMOCRACY':
            votes_idle = 0
            votes_digging = 0

            for feature_count in range(len(centroid_window)//3):
                fc = feature_count

                distance_idle = sqrt(mean_squared_error(centroid_window[fc*3:(fc+1)*3-1], self.__CENTROID_IDLE_AG[fc*3:(fc+1)*3-1]))
                distance_digging = sqrt(mean_squared_error(centroid_window[fc*3:(fc+1)*3-1], self.__CENTROID_DIGGING_AG[fc*3:(fc+1)*3-1])) 

                if distance_idle<=distance_digging:
                    votes_idle += 1
                elif distance_digging<=distance_idle:
                    votes_digging += 1
            
            # vote count
            if votes_idle<=votes_digging:
                return 'DIGGING-AG'
        
        return 'IDLE-AG'
    
    # prediction
    def classifyActivity(self, window, deployment, speed):
 
        status = 'IDLE'
    
        if deployment is 'Agricultural':
            status = self.__ag_algorithm(window, deployment)
                
        elif deployment is 'Excavator':
            status = self.__ex_algorithm(window, deployment)
            try:
                if float(speed)>4:
                    status = 'DRIVING'
                elif float(speed)<0.2 and status =='DRIVING':
                    status = 'DIGGING'
            except:
                status = status
                    
        elif deployment is 'Backhoe':
            status = self.__ex_algorithm(window, deployment)
            try:
                if float(speed)>4:
                    status = 'DRIVING'
                elif float(speed)<0.2 and status =='DRIVING':
                    status = 'DIGGING'
            except:
                status = status
            
        return status