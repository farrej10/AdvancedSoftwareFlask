import unittest
import app as ap

class Testing(unittest.TestCase):
    
   
    def test_0_busroutes(self):
        
        self.assertEqual(ap.busroutes(), ('Bad Request',400))
    
    def test_0_status(self):
        
        a = ap.status()
        currentDT = datetime.datetime.now()
        currentMinute = currentDT.minute
        statusDict={}
        if currentMinute >= 0 and currentMinute < 15:
            statusDict['bus'] = True
            statusDict['luas'] = True

        if (currentMinute >= 15 ) and (currentMinute < 30):
            statusDict['bus'] = True
            statusDict['luas'] = False

        if (currentMinute >= 30 ) and (currentMinute < 45):
            statusDict['bus'] = False
            statusDict['luas'] = True
	
        if (currentMinute >= 45 ) and (currentMinute < 60):
            statusDict['bus'] = False
            statusDict['luas'] = False

        self.assertEqual(a, statusDict)

    def test_0_getcoords(self):
        f= open("getcoords.json")
        data = json.load(f)
        self.assertEqual(ap.get_coordinates, data)    

    def test_0_update(self):
        
        self.assertEqual(ap.update(), ('',204))

    def test_0_luas(self):
        f = open("luas.csv","r")
        
        contents = f.read()

        self.assertEqual(ap.luas(), contents)

    def test_0_bus(self):
        f = open("bus.csv","r")
        
        contents = f.read()

        self.assertEqual(ap.bus(), contents)

    def test_0_rail(self):
        f = open("rail.csv","r")
        
        contents = f.read()

        self.assertEqual(ap.rail(), contents)






if __name__ == '__main__':
    unittest.main()