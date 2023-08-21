###############################################################
###############################################################
# Author                  Raghunath J, revised by Bambi Brewer
#                         and Kristina Lauwers
# Last Edit Date          11/20/2019
# Description             This python file contains Microbit, 
# Hummingbird, and Finch classes.
# The Microbit class controls a micro:bit via bluetooth. It
# includes methods to print on the micro:bit LED array or set
# those LEDs individually. It also contains methods to read the
# values of the micro:bit accelerometer and magnetometer.
# The Hummingbird class extends the Microbit class to incorporate
# functions to control the inputs and outputs of the Hummingbird
# Bit. It includes methods to set the values of motors and LEDs,
# as well as methods to read the values of the sensors.
# The Finch class also extends the Microbit class. This class
# similarly includes function to control the inputs and outputs
# of the Finch robot.
###############################################################
###############################################################
import urllib.request
import sys
import time
###############################################################
###############################################################
#Constants 

CHAR_FLASH_TIME = 0.3        #Character Flash time

# Error strings
CONNECTION_SERVER_CLOSED = "Error: Request to device failed"
NO_CONNECTION = "Error: The device is not connected"

#Calculations after receveing the raw values for Hummingbird
DISTANCE_FACTOR          = 117/100
SOUND_FACTOR             = 200/255
DIAL_FACTOR              = 100/230
LIGHT_FACTOR             = 100/255 
VOLTAGE_FACTOR            = 3.3/255

#Scaling factors for Finch
BATTERY_FACTOR = 0.0406

TEMPO                      = 60

###############################################################

class Microbit:
    """Microbit Class includes the control of the outputs and inputs
    present on the micro:bit."""
        
        #Test requests to find the devices connected
    base_request_out = "http://127.0.0.1:30061/hummingbird/out"
    base_request_in  = "http://127.0.0.1:30061/hummingbird/in"
    stopall          = "http://127.0.0.1:30061/hummingbird/out/stopall"
    
    symbolvalue      =  None


    ##################################################################################
    #######################     UTILITY FUNCTIONS      ###############################
    ##################################################################################
    

    
    def __init__(self, device = 'A'):
        """Called when the class is initialized."""
                
        #Check if the letter of the device is valid, exit otherwise
        if('ABC'.find(device) != -1):
            self.device_s_no = device
            # Check if the device is connected and if it is a micro:bit
            if not self.isConnectionValid(): 
                self.stopAll()
                sys.exit()
            
            if not self.isMicrobit():        # it isn't a micro:bit
                print("Error: Device " + str(self.device_s_no) + " is not a micro:bit")
                self.stopAll()
                sys.exit()
            self.symbolvalue = [0]*25
        else:
            print("Error: Device must be A, B, or C.")
            self.stopAll()
            sys.exit()
        

    def isConnectionValid(self):
        """This function tests a connection by attempting to read whether or
        not the micro:bit is shaking. Return true if the connection is good
        and false otherwise."""
                
        http_request = self.base_request_in + "/" + "orientation" + "/" + "Shake" + "/" +str(self.device_s_no)
        try :
            response_request =  urllib.request.urlopen(http_request)
        except:
            print(CONNECTION_SERVER_CLOSED)
            return False
        response = response_request.read().decode('utf-8')

        if(response == "Not Connected"):
            print("Error: Device " + str(self.device_s_no) + " is not connected")
            return False
        return True

    
    def isMicrobit(self):
        """This function determines whether or not the device is a micro:bit."""

        http_request = self.base_request_in + "/isMicrobit/static/" + str(self.device_s_no) 
        response = self._send_httprequest(http_request)

        # Old versions of BlueBird Connector don't support this request 
        if (response != ""):
            return (response == 'true')
        else:
            # Try to read sensor 4. The value will be 255 for a micro:bit (there is no sensor 4)
            # And some other value for the Hummingbird
            http_request = self.base_request_in + "/" + "sensor" + "/4/" +str(self.device_s_no)
            response = self._send_httprequest(http_request)

            return (response == "255")

    
    def clampParametersToBounds(self, input, inputMin, inputMax):
        """This function checks whether an input parameter is within the
        given bounds. If not, it prints a warning and returns a value of the
        input parameter that is within the required range. Otherwise, it
        just returns the initial value."""
                
        if ((input < inputMin) or (input > inputMax)):
            print("Warning: Please choose a parameter between " + str(inputMin) + " and " + str(inputMax))
            return max(inputMin, min(input, inputMax))
        else:
            return input

    
    def process_display(self , value):
        """Convert a string of 1's and 0's into true and false."""
                
        new_str = ""
        for letter in value:
            if(letter == 0):
                new_str += "false/"
            else:                    #All nonzero values become true
                new_str += "true/"
        
        # Remove the last character in a string
        new_str = new_str[:len(new_str)-1]
        return new_str


    @staticmethod
    def __constrainToInt(number):
        """Utility function to ensure number is an integer. Will round and cast to int
        (with warning) if necessary."""

        if not isinstance(number, int):
            oldNumber = number
            number = int(round(number))
            print("Warning: Parameter must be an integer. Using " + str(number) + " instead of " + str(oldNumber) + ".")

        return number

        
    ######################################################################
    #######################  OUTPUTS MICRO BIT ###########################
    ######################################################################
    
    def setDisplay(self, LEDlist):
        """Set Display of the LED Array on microbit with the given input LED
        list of 0's and 1's."""
                
        #Check if LED_string is valid to be printed on the display
        #Check if the length of the array to form a symbol not equal than 25
        if(len(LEDlist) != 25):
            print("Error: setDisplay() requires a list of length 25")
            return             # if the array is the wrong length, don't want to do anything else
        
        #Check if all the characters entered are valid
        for index in range(0,len(LEDlist)):
            LEDlist[index] = self.clampParametersToBounds(LEDlist[index],0,1) 
        
        # Reset the display status
        self.symbolvalue = LEDlist

        #Convert the LED_list to  an appropriate value which the server can understand
        LED_string = self.process_display(LEDlist)
        #Send the http request
        response = self.send_httprequest_micro("symbol",LED_string)
        return response
    
    
    def print(self, message):
        """Print the characters on the LED screen."""
        
        # Warn the user about any special characters - we can mostly only print English characters and digits
        for letter in message:
            if not (((letter >= 'a') and (letter <= 'z')) or ((letter >= 'A') and (letter <= 'Z')) or ((letter >= '0') and (letter <= '9')) or (letter == ' ')):
                print("Warning: Many special characters cannot be printed on the LED display")

        # Need to replace spaces with %20
        message = message.replace(' ','%20')

        # Empty out the internal representation of the display, since it will be blank when the print ends
        self.symbolvalue = [0]*25

        #Send the http request
        response = self.send_httprequest_micro("print",message)
        return response
    
    
    
    def setPoint(self, x , y , value):
        """Choose a certain LED on the LED Array and switch it on or off.
        The value specified should be 1 for on, 0 for off."""
                
        #Check if x, y and value are valid
        x = self.clampParametersToBounds(x,1,5)
        y = self.clampParametersToBounds(y,1,5)
        value = self.clampParametersToBounds(value,0,1)
        
        #Calculate which LED should be selected
        index = (x-1)*5 + (y-1)
        
        # Update the state of the LED displayf
        self.symbolvalue[index] = value
        
        #Convert the display status to  an appropriate value which the server can understand
        outputString = self.process_display(self.symbolvalue)

        #Send the http request
        response = self.send_httprequest_micro("symbol",outputString)
        return response


    def playNote(self, note, beats):
        """Make the buzzer play a note for certain number of beats. Note is the midi
        note number and should be specified as an integer from 32 to 135. Beats can be
        any number from 0 to 16. One beat corresponds to one second."""
    
        #Check that both parameters are within the required bounds
        note = self.clampParametersToBounds(note, 32, 135)
        beats = self.clampParametersToBounds(beats, 0, 16)

        note = self.__constrainToInt(note)
        beats = int(beats * (60000/TEMPO))
    
        #Send HTTP request
        #response = self.__send_httprequest_out("playnote", note, beats)
        http_request = self.base_request_out + "/playnote/" + str(note) + "/" + str(beats) + "/" + str(self.device_s_no)
        response = self._send_httprequest(http_request)
        return response



    ##############################################################################
    ############################## INPUTS MICROBIT ###############################
    ##############################################################################
    
    
    def _getXYZvalues(self, sensor, intResult):
        """Return the X, Y, and Z values of the given sensor."""
        
        dimension = ['X','Y','Z']
        values = []  
        
        for i in range(0,3):
            #Send HTTP request
            response = self.send_httprequest_micro_in(sensor, dimension[i])
            if intResult:
                values.append(int(response))
            else:
                values.append(round(float(response), 3))
        
        return (values[0],values[1],values[2])
    

    def getAcceleration(self):
        """Gives the acceleration of X,Y,Z in m/sec2."""

        return self._getXYZvalues("Accelerometer", False)
    
    
    def getCompass(self):
        """Returns values 0-359 indicating the orentation of the Earth's
        magnetic field."""  
                
        #Send HTTP request
        response = self.send_httprequest_micro_in("Compass",None)
        compass_heading = int(response)
        return compass_heading

    
    def getMagnetometer(self):
        """Return the values of X,Y,Z of a magnetommeter."""

        return self._getXYZvalues("Magnetometer", True)

    
    def getButton(self,button):
        """Return the status of the button asked. Specify button 'A', 'B', or
        'Logo'. Logo available for V2 micro:bit only."""
                
        button = button.upper()
        #Check if the button A and button B are represented in a valid manner
        if((button != 'A') and (button != 'B') and (button != 'LOGO')):
            print("Error: Button must be A, B, or Logo.")
            sys.exit()
        #Send HTTP request
        response = self.send_httprequest_micro_in("button", button)
        #Convert to boolean form
        if(response == "true"):
            button_value = True
        elif(response == "false"):
            button_value = False
        else:
            print("Error in getButton: " + response)
            sys.exit()
        
        return button_value


    def getSound(self):
        """Return the current sound level as an integer between 1 and 100.
        Available for V2 micro:bit only."""

        response = self.send_httprequest_micro_in("V2sensor", "Sound")

        try:
            value = int(response)
        except:
            print ("Error in getSound: " + response)
            sys.exit()

        return value


    def getTemperature(self):
        """Return the current temperature as an integer in degrees Celcius.
        Available for V2 micro:bit only."""

        response = self.send_httprequest_micro_in("V2sensor", "Temperature")

        try:
            value = int(response)
        except:
            print ("Error in getTemperature: " + response)
            sys.exit()

        return value

    
    def isShaking(self):
        """Return true if the device is shaking, false otherwise."""
                
        #Send HTTP request
        response = self.send_httprequest_micro_in("Shake",None)
        if(response == "true"):        # convert to boolean
            shake = True
        else:
            shake = False
        
        return shake

    
    def getOrientation(self):
        """Return the orentation of the micro:bit. Options include:
        "Screen up", "Screen down", "Tilt left", "Tilt right", "Logo up",
        "Logo down", and "In between"."""
                
        orientations = ["Screen%20Up","Screen%20Down","Tilt%20Left","Tilt%20Right","Logo%20Up","Logo%20Down"]
        orientation_result = ["Screen up","Screen down","Tilt left","Tilt right","Logo up","Logo down"]
        
        #Check for orientation of each device and if true return that state
        for targetOrientation in orientations:
            response = self.send_httprequest_micro_in(targetOrientation,None)
            if(response == "true"):
                return orientation_result[orientations.index(targetOrientation)]
        
        #If we are in a state in which none of the above seven states are true
        return "In between"
    
    
    def stopAll(self):
        """Stop all device outputs (ie. Servos, LEDs, LED Array, Motors, etc.)."""
        
        time.sleep(0.1)         # Hack to give stopAll() time to act before the end of a program
        response = self.send_httprequest_stopAll()
        self.symbolvalue = [0]*25
        return response
    

    ##########################################################################
    ####################### SEND HTTP REQUESTS ###############################
    ##########################################################################

    def _send_httprequest(self, http_request):
        """Send an HTTP request and return the result."""
        try :
            response_request =  urllib.request.urlopen(http_request)
        except:
            print(CONNECTION_SERVER_CLOSED)
            sys.exit();

        response = response_request.read().decode('utf-8')
        if(response == "Not Connected"):
            print(NO_CONNECTION)
            sys.exit()

        time.sleep(0.01)        # Hack to prevent http requests from overloading the BlueBird Connector
        return response
    
    
    def send_httprequest_micro(self, peri , value):
        """Utility function to arrange and send the http request for microbit output functions."""
        
        #Print command
        if(peri == "print"):
            http_request = self.base_request_out + "/" + peri +  "/" + str(value)   + "/" + str(self.device_s_no)
        elif(peri == "symbol"):
            http_request = self.base_request_out + "/" + peri +  "/"  + str(self.device_s_no)  + "/" + str(value)
        try :
            response_request =  urllib.request.urlopen(http_request)
            if(response_request.read() == b'200'):
                response = 1
            else :
                response = 0
        except:
            print(CONNECTION_SERVER_CLOSED)
            sys.exit()
        time.sleep(0.01)        # Hack to prevent http requests from overloading the BlueBird Connector
        return response
 
    
    def send_httprequest_micro_in(self, peri , value):
        """Utility function to arrange and send the http request for microbit input functions."""
        
        if(peri == "Accelerometer"):
            http_request = self.base_request_in + "/" + peri +  "/" + str(value)   + "/" + str(self.device_s_no)
        elif(peri == "Compass"):
            http_request = self.base_request_in + "/" + peri + "/" + str(self.device_s_no)
        elif(peri == "Magnetometer"):
            http_request = self.base_request_in + "/" + peri + "/" + str(value)   + "/"+str(self.device_s_no)
        elif(peri == "button"):
            http_request = self.base_request_in + "/" + peri + "/" + str(value)   + "/"+str(self.device_s_no)
        elif(peri == "Shake"):
            http_request = self.base_request_in + "/" + "orientation" + "/" + peri + "/" +str(self.device_s_no)
        elif(peri == "Screen%20Up"):
            http_request = self.base_request_in + "/" + "orientation" + "/" + peri + "/" +str(self.device_s_no)
        elif(peri == "Screen%20Down"):
            http_request = self.base_request_in + "/" + "orientation" + "/" + peri + "/" +str(self.device_s_no)
        elif(peri == "Tilt%20Right"):
            http_request = self.base_request_in + "/" + "orientation" + "/" + peri + "/" +str(self.device_s_no)
        elif(peri == "Tilt%20Left"):
            http_request = self.base_request_in + "/" + "orientation" +  "/" + peri + "/" +str(self.device_s_no)
        elif(peri == "Logo%20Up"):
            http_request = self.base_request_in + "/" + "orientation" + "/" + peri + "/" +str(self.device_s_no)
        elif(peri == "Logo%20Down"):
            http_request = self.base_request_in + "/" + "orientation" + "/" + peri + "/" +str(self.device_s_no)
        else:
            http_request = self.base_request_in + "/" + peri +  "/" + str(value)   + "/" + str(self.device_s_no)
            
        try :
            response_request =  urllib.request.urlopen(http_request)
        except:
            print(CONNECTION_SERVER_CLOSED)
            sys.exit();
        response = response_request.read().decode('utf-8')
        if(response == "Not Connected"):
            print(NO_CONNECTION)
            sys.exit()
        time.sleep(0.01)        # Hack to prevent http requests from overloading the BlueBird Connector
        return response

    
    def send_httprequest_stopAll(self):
        """Send HTTP request for hummingbird bit output."""
            
        #Combine diffrenet strings to form a HTTP request
        http_request = self.stopall + "/" +str(self.device_s_no)
        try :
            response_request =  urllib.request.urlopen(http_request)
        except:
            print(CONNECTION_SERVER_CLOSED)
            sys.exit();
        if(response_request.read() == b'200'):
            response = 1
        else :
            response = 0
        time.sleep(0.01)        # Hack to prevent http requests from overloading the BlueBird Connector
        return response
    
    ######## END class Microbit ########


class Hummingbird(Microbit):
    """Hummingbird Bit Class includes the control of the outputs and inputs
        present on the Hummingbird Bit."""    

    ##########################################################################
    ######################  UTILITY FUNCTIONS ################################
    ##########################################################################

    def __init__(self , device = 'A'):
        """Class initializer. Specify device letter A, B or C."""

        #Check if the length of the array to form a symbol is greater than 25"""
        if('ABC'.find(device) != -1):
            self.device_s_no = device
            # Check if device is connected and is a hummingbird
            if not self.isConnectionValid(): 
                self.stopAll()
                sys.exit()
            if not self.isHummingbird():
                print("Error: Device " + str(self.device_s_no) + " is not a Hummingbird")
                self.stopAll()
                sys.exit()
            self.symbolvalue = [0]*25
        else:
            self.stopAll()
            sys.exit()


    def isHummingbird(self):
        """This function determines whether or not the device is a Hummingbird."""

        http_request = self.base_request_in + "/isHummingbird/static/" + str(self.device_s_no) 
        response = self._send_httprequest(http_request)

        # Old versions of BlueBird Connector don't support this request 
        if (response != ""):
            return (response == 'true')
        else:
            # Try to read sensor 4. The value will be 255 for a micro:bit (there is no sensor 4)
            # And some other value for the Hummingbird
            http_request = self.base_request_in + "/" + "sensor" + "/4/" +str(self.device_s_no)
            response = self._send_httprequest(http_request)

            return (response != "255")
            

    def isPortValid(self, port, portMax):
        """This function checks whether a port is within the given bounds.
        It returns a boolean value that is either true or false and prints
        an error if necessary."""
        
        if ((port < 1) or (port > portMax)):
            print("Error: Please choose a port value between 1 and " + str(portMax))
            return False
        else:
            return True    

    
    def calculate_LED(self,intensity):
        """ Utility function to covert LED from 0-100 to 0-255."""
        
        intensity_c = int((intensity * 255) / 100) ;
        
        return intensity_c

    
    def calculate_RGB(self,r_intensity, g_intensity, b_intensity):
        """Utility function to covert RGB LED from 0-100 to 0-255."""
        
        r_intensity_c   = int((r_intensity * 255) / 100) ;
        g_intensity_c   = int((g_intensity * 255) / 100) ;
        b_intensity_c    = int((b_intensity * 255) / 100) ;
        
        return (r_intensity_c,g_intensity_c,b_intensity_c)

    
    def calculate_servo_p(self,servo_value):
        """Utility function to covert Servo from 0-180 to 0-255."""
        
        servo_value_c   = int((servo_value * 254)/180) ;
        
        return servo_value_c

    
    def calculate_servo_r(self,servo_value):
        """Utility function to covert Servo from -100 - 100 to 0-255."""
        
        #If the vlaues are above the limits fix the instensity to maximum value,
        #if less than the minimum value fix the intensity to minimum value
        if ((servo_value>-10) and (servo_value<10)):
            servo_value_c = 255
        else:
            servo_value_c = int(( servo_value*23 /100) + 122)
        return servo_value_c


    ##############################################################################
    ########################### HUMMINGBIRD BIT OUTPUT ###########################
    ##############################################################################

    
    def setLED(self, port, intensity):
        """Set LED  of a certain port requested to a valid intensity."""
            
        # Early return if we can't execute the command because the port is invalid
        if not self.isPortValid(port,3):
            return

        #Check the intensity value lies with in the range of LED limits
        intensity = self.clampParametersToBounds(intensity,0,100)

        #Change the range from 0-100 to 0-255
        intensity_c = self.calculate_LED(intensity)
        #Send HTTP request
        response    = self.send_httprequest("led" , port , intensity_c)
        return response
    

    
    def setTriLED(self, port, redIntensity, greenIntensity, blueIntensity):
        """Set TriLED  of a certain port requested to a valid intensity."""
        
        # Early return if we can't execute the command because the port is invalid
        if not self.isPortValid(port,2):
            return
        
        #Check the intensity value lies with in the range of RGB LED limits
        red = self.clampParametersToBounds(redIntensity,0,100)
        green = self.clampParametersToBounds(greenIntensity,0,100)
        blue = self.clampParametersToBounds(blueIntensity,0,100)
        
        #Change the range from 0-100 to 0-255
        (r_intensity_c, g_intensity_c, b_intensity_c) = self.calculate_RGB(red,green,blue)
        #Send HTTP request
        response = self.send_httprequest("triled" , port , str(r_intensity_c)+ "/" + str(g_intensity_c) +"/" + str(b_intensity_c))
        return response

    
    def setPositionServo(self, port, angle):
        """Set Position servo of a certain port requested to a valid angle."""
        
        # Early return if we can't execute the command because the port is invalid
        if not self.isPortValid(port,4):
            return

        #Check the angle lies within servo limits
        angle = self.clampParametersToBounds(angle,0,180)

        angle_c = self.calculate_servo_p(angle)
        #Send HTTP request
        response = self.send_httprequest("servo" , port , angle_c)
        return response

    
    def setRotationServo(self, port, speed):
        """Set Rotation servo of a certain port requested to a valid speed."""
            
        # Early return if we can't execute the command because the port is invalid
        if not self.isPortValid(port,4):
            return

        #Check the speed lies within servo limits
        speed = self.clampParametersToBounds(speed,-100,100)

        speed_c  = self.calculate_servo_r(speed)
        #Send HTTP request 
        response = self.send_httprequest("rotation", port, speed_c)
        return response
    

    
    ############################################################################
    ########################### HUMMINGBIRD BIT INPUT ##########################
    ############################################################################

    def getSensor(self,port):
        """Read the value of the sensor attached to a certain port.
        If the port is not valid, it returns -1."""
            
        # Early return if we can't execute the command because the port is invalid
        if not self.isPortValid(port,3):
            return -1

        response       = self.send_httprequest_in("sensor",port)
        return response
    
    
    def getLight(self, port):
        """Read the value of the light sensor attached to a certain port."""
        
        response = self.getSensor(port)
        light_value    = int(response * LIGHT_FACTOR)
        return light_value

    
    def getSound(self, port):
        """Read the value of the sound sensor attached to a certain port."""

        if port == "microbit" or port == "micro:bit" or port == "Microbit":
            return Microbit.getSound(self)
        
        response = self.getSensor(port)
        sound_value    = int(response *SOUND_FACTOR)
        return sound_value

    
    def getDistance(self, port):
        """Read the value of the distance sensor attached to a certain port."""
        
        response = self.getSensor(port)
        distance_value    = int(response * DISTANCE_FACTOR)
        return distance_value

    
    def getDial(self, port):
        """Read the value of the dial attached to a certain port."""
        
        response       = self.getSensor(port)
        dial_value    = int(response *DIAL_FACTOR)
        if(dial_value > 100):
            dial_value = 100
        return dial_value

    
    def getVoltage(self, port):
        """Read the value of  the dial attached to a certain port."""
        
        response       = self.getSensor(port)
        voltage_value    = response *VOLTAGE_FACTOR
        return voltage_value
    
    
    ###########################################################################
    ########################### SEND HTTP REQUESTS ############################
    ###########################################################################
    
    def send_httprequest_in(self, peri, port):
        """Send HTTP requests for Hummingbird bit inputs."""
            
        #Combine different strings to form an HTTP request
        http_request = self.base_request_in + "/" + peri    + "/" + str(port) + "/" + str(self.device_s_no) 
        try :
            response_request =  urllib.request.urlopen(http_request)
        except:
            print(CONNECTION_SERVER_CLOSED)
            sys.exit();
        response = response_request.read().decode('utf-8')
        if(response == "Not Connected"):
            print(NO_CONNECTION)
            sys.exit()
        time.sleep(0.01)        # Hack to prevent http requests from overloading the BlueBird Connector
        return int(response)

    
    def send_httprequest(self, peri, port , value):
        """Send HTTP request for Hummingbird bit output"""
            
        #Combine different strings to form an HTTP request
        http_request = self.base_request_out + "/" + peri    + "/" + str(port) +  "/" + str(value)   + "/" + str(self.device_s_no) 
        try :
            response_request =  urllib.request.urlopen(http_request)
        except:
            print(CONNECTION_SERVER_CLOSED)
            sys.exit();
        if(response_request.read() == b'200'):
            response = 1
        else :
            response = 0
        time.sleep(0.01)        # Hack to prevent http requests from overloading the BlueBird Connector
        return response


    
    ######## END class Hummingbird ########


class Finch(Microbit):
    """The Finch class includes the control of the outputs and inputs present
    in the Finch robot. When creating an instance, specify which robot by the
    device letter used in the BlueBirdConnector device list (A, B, or C)."""
    
    def __init__(self , device = 'A'):
        """Class initializer. """

        if('ABC'.find(device) != -1): #check for valid device letter
            self.device_s_no = device

            if not self.isConnectionValid():
                self.__exit("Error: Invalid Connection")
            
            if not self.__isFinch():    
                self.__exit("Error: Device " + str(self.device_s_no) + " is not a Finch")

            self.symbolvalue = [0]*25

        else:
            self.__exit("Error: Device must be A, B, or C.")

        
    ######## Finch Utility Functions ########

    def __exit(self, msg):
        """Print error, shutdown robot, and exit python"""
        print(msg)
        self.stopAll()
        sys.exit()


    def __isFinch(self):
        """Determine whether or not the device is a Finch"""
        http_request = self.base_request_in + "/isFinch/static/" + str(self.device_s_no) 
        response = self._send_httprequest(http_request)
    
        return (response == 'true')


    @staticmethod    
    def __calculate_RGB(r_intensity, g_intensity, b_intensity):
        """Utility function to covert RGB LED from 0-100 to 0-255"""
        r_intensity_c = int((r_intensity * 255) / 100)
        g_intensity_c = int((g_intensity * 255) / 100)
        b_intensity_c = int((b_intensity * 255) / 100)
        
        return (r_intensity_c, g_intensity_c, b_intensity_c)


    @staticmethod
    def __formatRightLeft(direction):
        """Utility function to format a selection of right or left for a backend request."""
        if direction == "R" or direction == "r" or direction == "Right" or direction == "right":
            return "Right"
        elif direction == "L" or direction == "l" or direction == "Left" or direction == "left":
            return "Left"
        else:
            print("Error: Please specify either 'R' or 'L' direction.")
            return None


    @staticmethod
    def __formatForwardBackward(direction):
        """Utility function to format a selection of forward or backward for a backend request."""
        if direction == "F" or direction == "f" or direction == "Forward" or direction == "forward":
            return "Forward"
        elif direction == "B" or direction == "b" or direction == "Backward" or direction == "backward":
            return "Backward"
        else:
            print("Error: Please specify either 'F' or 'B' direction.")
            return None
        

    def __send_httprequest_in(self, peri, port):
        """Send HTTP requests for Finch inputs.
        Combine strings to form a HTTP input request.
        Send the request and return the result as a string.""" 
        http_request = self.base_request_in + "/" + peri    + "/" + str(port) + "/" + str(self.device_s_no) 
        response = self._send_httprequest(http_request)
        return response


    def __send_httprequest_out(self, arg1, arg2, arg3):
        """Send HTTP request for Finch output.
        Combine strings to form a HTTP output request.
        Send the request and return 1 if successful, 0 otherwise."""
        
        requestString = "/" + arg1 + "/"
        if not (arg2 is None):
                requestString = requestString + str(arg2) + "/"
        if not (arg3 is None):
                requestString = requestString + str(arg3) + "/"
            
        http_request = self.base_request_out + requestString + str(self.device_s_no) 
        response = self._send_httprequest(http_request)

        if(response == "200"):
                return 1
        else :
                return 0


    def __send_httprequest_move(self, arg1, arg2, arg3, arg4):
        """Send HTTP request to move the Finch.
        Combine strings to form a HTTP output request.
        Send the request and return 1 if successful, 0 otherwise."""
        
        requestString = "/" + arg1 + "/" + str(self.device_s_no) + "/" + str(arg2) + "/"
        if not (arg3 is None):
                requestString = requestString + str(arg3) + "/"
        if not (arg4 is None):
                requestString = requestString + str(arg4) + "/"
            
        http_request = self.base_request_out + requestString
        response = self._send_httprequest(http_request)

        if(response == "200"):
                return 1
        else :
                return 0


    ######## Finch Output ########

    def __setTriLED(self, port, redIntensity, greenIntensity, blueIntensity):
        """Set TriLED(s) on the Finch.
        Port 1 is the beak. Ports 2 to 5 are tail. Specify port "all" to set the whole tail."""

        #Early return if we can't execute the command because the port is invalid
        if ((not port == "all") and ((port < 1) or (port > 5))):
                return 0

        #Check the intensity value lies with in the range of RGB LED limits
        red = self.clampParametersToBounds(redIntensity,0,100)
        green = self.clampParametersToBounds(greenIntensity,0,100)
        blue = self.clampParametersToBounds(blueIntensity,0,100)
        
        #Change the range from 0-100 to 0-255
        (red_c, green_c, blue_c) = self.__calculate_RGB(red,green,blue)

        #Send HTTP request
        intensityString = str(red_c)+ "/" + str(green_c) +"/" + str(blue_c)
        response = self.__send_httprequest_out("triled", port, intensityString)
        return response
    
    
    def setBeak(self, redIntensity, greenIntensity, blueIntensity):
        """Set beak to a valid intensity. Each intensity should be an integer from 0 to 100."""
        
        response = self.__setTriLED(1, redIntensity, greenIntensity, blueIntensity)
        return response


    def setTail(self, port, redIntensity, greenIntensity, blueIntensity):
        """Set tail to a valid intensity. Port can be specified as 1, 2, 3, 4, or all.
        Each intensity should be an integer from 0 to 100."""
        
        #Triled port 1 is the beak. Tail starts counting at 2
        if not port == "all":
                port = port + 1
    
        response = self.__setTriLED(port, redIntensity, greenIntensity, blueIntensity)
        return response


    def __moveFinchAndWait(self, motion, direction, length, speed):
        """Send a command to move the finch and wait until the finch has finished
        its motion to return. Used by setMove and setTurn."""

        isMoving = self.__send_httprequest_in("finchIsMoving", "static")
        wasMoving = isMoving
        commandSendTime = time.time()
        done = False

        #Send HTTP request
        response = self.__send_httprequest_move(motion, direction, length, speed)

        while (not(done) and not(isMoving == "Not Connected")):
            wasMoving = isMoving
            time.sleep(0.01)
            isMoving = self.__send_httprequest_in("finchIsMoving", "static")
            done = ((time.time() > commandSendTime + 0.5) or (wasMoving == "true")) and (isMoving == "false")

        return response


    def setMove(self, direction, distance, speed):
        """Move the Finch forward or backward for a given distance at a given speed.
        Direction should be specified as 'F' or 'B'."""

        direction = self.__formatForwardBackward(direction)
        if direction is None:
                return 0

        distance = self.clampParametersToBounds(distance, -10000, 10000)
        speed =  self.clampParametersToBounds(speed, 0, 100)

        response = self.__moveFinchAndWait("move", direction, distance, speed)

        return response


    def setTurn(self, direction, angle, speed):
        """Turn the Finch right or left to a given angle at a given speed.
        Direction should be specified as 'R' or 'L'."""

        direction = self.__formatRightLeft(direction)
        if direction is None:
                return 0

        angle =  self.clampParametersToBounds(angle, -360000, 360000)
        speed =  self.clampParametersToBounds(speed, 0, 100)

        response = self.__moveFinchAndWait("turn", direction, angle, speed)

        return response


    def setMotors(self, leftSpeed, rightSpeed):
        """Set the speed of each motor individually. Speed should be in
        the range of -100 to 100."""

        leftSpeed = self.clampParametersToBounds(leftSpeed, -100, 100)
        rightSpeed = self.clampParametersToBounds(rightSpeed, -100, 100)
                 
        #Send HTTP request
        response = self.__send_httprequest_move("wheels", leftSpeed, rightSpeed, None)
        return response


    def stop(self):
        """Stop the Finch motors."""

        #Send HTTP request
        response = self.__send_httprequest_out("stopFinch", None, None)
        return response


    def resetEncoders(self):
        """Reset both encoder values to 0."""
        response = self.__send_httprequest_out("resetEncoders", None, None)

        #The finch needs a chance to actually reset
        time.sleep(0.2)
        
        return response
        

    ######## Finch Inputs ########

    def __getSensor(self, sensor, port):
        """Read the value of the specified sensor. Port should be specified as either 'R'
        or 'L'. If the port is not valid, returns -1."""
        
        #Early return if we can't execute the command because the port is invalid
        if ((not sensor == "finchOrientation") and (not port == "Left") and (not port == "Right") and
            (not ((port == "static") and (sensor == "Distance" or sensor == "finchCompass")))):
                return -1

        response = self.__send_httprequest_in(sensor, port)
        return response


    def getLight(self, direction):
        """Read the value of the right or left light sensor ('R' or 'L')."""
        direction = self.__formatRightLeft(direction)
        if direction is None:
                return 0
        
        response = self.__getSensor("Light", direction)
        return int(response)

    
    def getDistance(self):
        """Read the value of the distance sensor"""
        response = self.__getSensor("Distance", "static")
        return int(response)


    def getLine(self, direction):
        """Read the value of the right or left line sensor ('R' or 'L').
        Returns brightness as a value 0-100 where a larger number
        represents more reflected light."""
        direction = self.__formatRightLeft(direction)
        if direction is None:
                return 0
        
        response = self.__getSensor("Line", direction)
        return int(response)


    def getEncoder(self, direction):
        """Read the value of the right or left encoder ('R' or 'L').
        Values are returned in rotations."""
        direction = self.__formatRightLeft(direction)
        if direction is None:
                return 0
        
        response = self.__getSensor("Encoder", direction)
        encoder_value = round(float(response), 2)
        return encoder_value


    # The following methods override those within the Microbit
    # class to return values within the Finch reference frame.

    def getAcceleration(self):
        """Gives the acceleration of X,Y,Z in m/sec2, relative
        to the Finch's position."""

        return self._getXYZvalues("finchAccel", False)
    
    
    def getCompass(self):
        """Returns values 0-359 indicating the orentation of the Earth's
        magnetic field, relative to the Finch's position."""  
                
        #Send HTTP request
        response = self.__getSensor("finchCompass", "static")
        compass_heading = int(response)
        return compass_heading
        
    
    def getMagnetometer(self):
        """Return the values of X,Y,Z of a magnetommeter, relative to the Finch's position."""

        return self._getXYZvalues("finchMag", True)


    def getOrientation(self):
        """Return the orentation of the Finch. Options include:
        "Beak up", "Beak down", "Tilt left", "Tilt right", "Level",
        "Upside down", and "In between"."""
                
        orientations = ["Beak%20Up","Beak%20Down","Tilt%20Left","Tilt%20Right","Level","Upside%20Down"]
        orientation_result = ["Beak up","Beak down","Tilt left","Tilt right","Level","Upside down"]
        
        #Check for orientation of each device and if true return that state
        for targetOrientation in orientations:
            response = self.__getSensor("finchOrientation", targetOrientation)
            if(response == "true"):
                return orientation_result[orientations.index(targetOrientation)]
        
        #If we are in a state in which none of the above seven states are true
        return "In between"


    ######## END class Finch ########
    
