class UAV:
    def __init__(self,x,y,B,fi):
        self.x = x
        self.y = y
        self.B = B
        self.fi = fi
        
    def b(self, t):
        t = (t + self.fi) % 10
        if t in [2,7]:
            return self.B
        elif t in [3,4,5,6]:
             return self.B/2
        else:
            return 0
 
class flow:
    def __init__(self ,f , x, y, t, Qtotal, m1, n1, m2, n2):
        self.f = f
        self.x = x
        self.y = y
        self.t = t
        self.Qtotal = Qtotal
        self.Q = Qtotal
        self.m1 = m1
        self.n1 = n1
        self.m2 = m2
        self.n2 = n2


with open("test_input.txt","r") as file:
    file = file.readlines()
    
    header = map(int,(file.pop(0).rstrip()).split(sep=' '))
    ### ODCZYTANIE : SZEROKOŚCI SIATKI (M) WYSOKOSCI SIATKI (N), ILOSC FLOWOW DO OBSLUZENIA (FN), CZAS SYMULACJI (T) ###
    M, N, FN, T = header
    
    ## UTWORZENIE PUSTEJ SIATKI
    topology = [[0 for _ in range(M)] for _ in range(N)]
    
    ### TWORZENIE SIATKI PELNEJ UAV O WYMIARACH M X N (KAZDY KOORDYNAT TO ODDZIELNY OBIEKT KLASY UAV)
    for row_index in range(M*N):
        readed_uav = UAV(*map(int,(file[row_index].rstrip()).split(sep=' ')))
        topology[readed_uav.y][readed_uav.x] = readed_uav
    
    ### PRINT KORDYNATOW SIATKI (TESTOWY)
    flows = []
    for row_index in range(M*N,len(file)):
        flows.append(flow(*map(int,(file[row_index].rstrip()).split(sep=' '))))

    UAV_list = []
    for row in topology:
        for uav in row:
            UAV_list.append([uav.x,uav.y,uav.B,uav.fi])
    uav_info = sorted(UAV_list, key=lambda e: (e[0], e[1]))
    
    flows = [[f.f,f.x,f.y,f.t,f.Qtotal,f.Q,f.m1,f.n1,f.m2,f.n2] for f in flows]