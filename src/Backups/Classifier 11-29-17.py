import numpy as np
import scipy

class Classifier:
    
    def __init__(self, windowsize):
        self.__WINDOWSIZE = windowsize
    
    # 7-point smoothing
    def __smooth(self,d):

        #for i in range(3,len(d)-3):
        #    d[i] = (d[i-3]+d[i-2]+d[i-1]+d[i]+d[i+1]+d[i+2]+d[i+3])/7

        return d
    
    #clustering algorithm based on eucledian distance 
    def __algorithm(self, window):

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

    def classifyActivity(self, window, speed):
 
        status = 'IDLE'

        if len(window)==self.__WINDOWSIZE:
               status = self.__algorithm(window)

	if float(speed)>4:
		status = 'DRIVING'

	if float(speed)<0.2 and status =='DRIVING':
		status = 'DIGGING'

        return status

