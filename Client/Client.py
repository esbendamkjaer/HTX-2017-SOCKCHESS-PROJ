#!/usr/bin/python3

import socket;

class Chessboard():

    columns = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H');

    symbols = ("X", "K", "D", "L", "S", "T", "B");
    colors = ("H", "S");

    def __init__(self):
        self.board = [
                ["X",   "X",    "X",    "X",    "X",    "X",    "X",    "X"],
                ["X",   "X",    "X",    "X",    "X",    "X",    "X",    "X"],
                ["X",   "X",    "X",    "X",    "X",    "X",    "X",    "X"],
                ["X",   "X",    "X",    "X",    "X",    "X",    "X",    "X"],
                ["X",   "X",    "X",    "X",    "X",    "X",    "X",    "X"],
                ["X",   "X",    "X",    "X",    "X",    "X",    "X",    "X"],
                ["X",   "X",    "X",    "X",    "X",    "X",    "X",    "X"],
                ["X",   "X",    "X",    "X",    "X",    "X",    "X",    "X"]
            ];

    def printChessboard(self, order):
        #Order bestemmer vis tur det er. True = Hvid; False = Sort;

        board = self.board;
        columns = Chessboard.columns;
        r = range(0, 8);

        if (not order):
            #Hvis det er sorts tur, placeres dennes brikker nederst / Brættet "vendes" både horizontalt og vertikalt.
            #Reversed-funktionen bruges, så klassevariablerne ikke forbliver ændret ved brug af .reverse().
            #Rækkerne vendes på x-aksen.
            board = reversed(board);
            r = range(7, -1, -1);

        print('\n', end='\t');
        for i in r:
            print(columns[i], end='\t');

        print('\n');

        #Enumerate bruges her til at gennemgå index og værdi samtidigt.
        for i, x in enumerate(board):
            if (order):
                print((i+1), end='\t');
            else:
                print(8-i, end='\t');

            if (not order):
                #Kolonnerne vendes på y-aksen.
                x = reversed(x);

            for j in x:
                print(j, end='\t');
            print("\n\n");

    def move(self, pos1, pos2):
        if (self.isEmpty(pos1)):
            print("Feltet er tomt.");
        else:
            pieceToMove = self.getPieceAtPos(pos1);
            self.setPieceAtPos(pos2, pieceToMove);
            self.emptySquare(pos1);

    def getPieceAtPos(self, pos):
        return self.board[(int(pos[1]) - 1)][Chessboard.columns.index(pos[0])];

    def setPieceAtPos(self, pos, piece):
        self.board[(int(pos[1]) - 1)][Chessboard.columns.index(pos[0])] = piece;

    def isEmpty(self, pos):
        piece = self.getPieceAtPos(pos);
        if (piece == "X"):
            return True;
        return False;

    def emptySquare(self, pos):
        self.setPieceAtPos(pos, "X");

    def onBoard(self, pos):
        xPos = Chessboard.columns.index(pos[0]) + 1;
        yPos = int(pos[1]);
        if (xPos < 1 or xPos > 8 or yPos > 8 or yPos < 1):
            return False;
        return True;

    @staticmethod
    def rawToPos(rawPos):
        #Når en position sendes over netværket sendes den som et tocifret tal hvoraf ét er x-koordinatet og ét er y-koordinatet.
        #Eksempelvis bliver "F4" til "53", da F er index 5 i columns-tuplen F -> 5, det andet ciffer er ét mindre end udgangspunktet 4 -> 3.
        #Der deles med ti og castes til heltal. 53 -> 5.3 -> 5;
        xPos = int((rawPos/10));
        #x-koordinatet ganges med 10 og trækkes fra rådataet. 5 -> 50; 53 - 50 = 3; 3 + 1 = 4;
        yPos = rawPos-(xPos*10) + 1;
        #Kolonnenavnet hentes fra columntuplen og sammensættes til y-koordinatet. 5 -> F; F + 4 = F4;
        return (Chessboard.columns[xPos] + str(yPos));

    @staticmethod
    def posToRaw(pos):
        xPos = Chessboard.columns.index(pos[0]);
        yPos = int(pos[1]) - 1;
        return xPos*10+yPos;

    @staticmethod
    def pieceToRaw(piece):
        #Her omdannes en streng for en brik til en tilsvarende talværdi.
        #Talværdierne for brikkerne har to cifre - én til farven (0-1) og én til symbolet (0-5).
        color = Chessboard.colors.index(piece[0]);
        symbol = Chessboard.symbols.index(piece[1]);
        return color * 10 + symbol;

    @staticmethod
    def rawToPiece(data):
        #Her omdannes et tal fra dataene til en tilsvarende tekstværdi for en brik
        color = int(data/10);
        symbol = data - color*10;
        return Chessboard.colors[color] + Chessboard.symbols[symbol];

    @staticmethod
    def boardToRaw(board):
        #I denne metode omdannes alle ikke-tomme felter til to talværdier - én for brikken og én for dens position.
        #Derefter omdannes talværdierne til bytes.

        data = bytes();

        for i in range(0, 8):
            for j in range(0, 8):
                rawPos = j*10+i;
                pos = Chessboard.rawToPos(rawPos);
                if (board.isEmpty(pos)):
                    continue;
                else:
                    data = data + bytes([Chessboard.pieceToRaw(board.getPieceAtPos(pos)), rawPos]);
        return data;

    @staticmethod
    def rawToBoard(data):
        board = Chessboard();
        for i in range(0, len(data), 2):
            rawPiece = data[i];
            rawPos = data[i+1];
            piece = Chessboard.rawToPiece(rawPiece);
            pos = Chessboard.rawToPos(rawPos);
            board.setPieceAtPos(pos, piece);
        return board;


class Packet():
    def __init__(self, packetID):
        self.packetID = bytes([packetID]);
    
    def sendData(self, sock):
        sock.send(self.getData());

    def getData(self):
        return self.packetID;

    #Jeg bruger en statisk metode, for at undgå at skulle oprette et objekt, for at bruge metoden. Dermed kan jeg tilgå metoden via Packet.parsePacket(...);
    @staticmethod
    def parsePacket(rawData):
        #Alle pakker starter med en byte, der er pakkeid'et.
        packetID = rawData[0];

        if (packetID == 0):
            #Packet00Login indeholder brugernavnslængden på byte 2.
            lengthOfUsername = rawData[1];
            #Packet00Login indeholder adgangskodelængden lige efter brugernavnslængden.
            lengthOfPassword = rawData[2 + lengthOfUsername];
            username = rawData[2:(2+lengthOfUsername)].decode("utf-8");
            password = rawData[(3+lengthOfUsername):(3+lengthOfUsername+lengthOfPassword)].decode("utf-8");
            return Packet00Login(username, password);
        elif (packetID == 1):
            validated = False;
            #LoginValidation indeholder en byte for validering af logininformation.
            if (rawData[1]):
                validated = True;
            return Packet01LoginValidation(validated);
        elif (packetID == 2):
            color = False;
            starting = False;
            #Packet02AssignColor indeholder en byte for farvetildeling samt om det er spillerens tur.
            if (rawData[1]):
                color = True;
            if (rawData[2]):
                starting = True;
            return Packet02AssignColor(color, starting);
        elif (packetID == 3):
            #Packet03Move indeholder to bytes - én for brikken der skal flyttes, og én for hvortil brikken skal flyttes.
            pos1 = Chessboard.rawToPos(rawData[1]);
            pos2 = Chessboard.rawToPos(rawData[2]);
            return Packet03Move(pos1, pos2);
        elif (packetID == 4):
            return Packet04InvalidMove();
        elif (packetID == 5):
            board = Chessboard.rawToBoard(rawData[1:]);
            return Packet05BoardStatus(board);


class Packet00Login(Packet):
    def __init__(self, username, password):
        self.username = username;
        self.password = password;
        super().__init__(0);

    def getData(self):
        #Jeg koder til Unicode før jeg bruger len-funktionen da et 'æ' eksempelvis fylder 2 bytes, og dermed tager to "pladser" efter kodningen.
        username = self.username.encode("utf-8");
        password = self.password.encode("utf-8");
        lengthOfUsername = bytes([len(username)]);
        lengthOfPassword = bytes([len(password)]);
        #Retunerer den rå pakkedata i et byteobjekt.
        return self.packetID + lengthOfUsername + username + lengthOfPassword + password;

class Packet01LoginValidation(Packet):
    def __init__(self, validated):
        super().__init__(1);
        self.validated = validated;

    def getData(self):
        temp = None;
        if self.validated:
            temp = bytes([1]);
        else:
            temp = bytes([0]);

        return self.packetID + temp;

class Packet02AssignColor(Packet):
    def __init__(self, color, starting):
        super().__init__(2)
        self.color = color;
        self.starting = starting;
        
    def getData(self):
        color = None;
        starting = None;

        if self.color:
            #1 for hvid/True
            color = bytes([1]);
        else:
            #0 for sort/False
            color = bytes([0]);

        if self.starting:
            #1 for spiller starter
            starting = bytes([1]);
        else:
            #0 for spiller starter ikke
            starting = bytes([0]);

        return self.packetID + color + starting;

class Packet03Move(Packet):

    def __init__(self, pos1, pos2):
        super().__init__(3);
        self.pos1 = pos1;
        self.pos2 = pos2;

    def getData(self):
        #Positionerne eksempelvis "B3" og "A1", bliver omdannet til et tal, så de kun fylder én byte hver.
        pos1 = Chessboard.posToRaw(self.pos1);
        pos2 = Chessboard.posToRaw(self.pos2);
        return self.packetID + bytes([pos1, pos2]);

class Packet04InvalidMove(Packet):
    def __init__(self):
        super().__init__(4);

class Packet05BoardStatus(Packet):
    symbols = ("X", "K", "D", "L", "S", "T", "B");
    colors = ("H", "S");

    def __init__(self, board):
        super().__init__(5);
        self.board = board;

    def getData(self):
        return self.packetID + Chessboard.boardToRaw(self.board);

class Client():
    import socket;
    import threading;
    import getpass;

    def __init__(self, host, port):
        self.host = host;
        self.port = port;
        self.sock = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM);
        self.sock.connect((host, port));

        self.running = True;

        self.board = Chessboard();
        self.order = False;

        self.validated = False;
        
        #Opretter to Thread instanser, og starter dem uden at gemme dem i en variabel.
        #Den første står får datamodtagning fra serveren.
        self.threading.Thread(target=self.receive).start();
        #Den anden står for brugerinput og dataafsending til serveren.
        self.threading.Thread(target=self.gameInput).start();

        #Eventobjekter som trådene bruger til at "kommunikere".
        self.WaitForValidationEvent = self.threading.Event();
        self.WaitForPacketMoveEvent = self.threading.Event();
        self.WaitForColorAssignmentEvent = self.threading.Event();

    def receive(self):
        #Makspakkestørrelse målt i bytes.
        size = 128;

        while (self.running):
            try:
                data = self.sock.recv(size);

                if (data):
                    packet = Packet.parsePacket(data);

                    #if-sætning der tjekker hvilken klasse, pakken er en instans af.
                    if (isinstance(packet, Packet01LoginValidation)):
                        if (packet.validated):
                            self.validated = True;
                        self.WaitForValidationEvent.set();
                    elif (isinstance(packet, Packet02AssignColor)):
                        self.order = packet.color;
                        if (packet.starting):
                            #Sæt MoveEvent til True, så der stoppes med at vente, da denne spiller starter / det er denne spillers tur.
                            self.WaitForPacketMoveEvent.set();
                        self.WaitForColorAssignmentEvent.set();
                    elif (isinstance(packet, Packet03Move)):
                        self.board.move(packet.pos1, packet.pos2);
                        self.board.printChessboard(self.order);
                        #Sæt MoveEvent til True, så der stoppes med at vente, eller bare springes over
                        self.WaitForPacketMoveEvent.set();
                    elif (isinstance(packet, Packet04InvalidMove)):
                        pass;
                    elif (isinstance(packet, Packet05BoardStatus)):
                        self.board = packet.board;
                else:
                    raise Exception("Forbindelse lukket af ektern vært.");
            except Exception as e:
                print(e.args);
                break;

    def gameInput(self):
        while (not self.validated):
            username = input("Brugernavn: ");
            password = self.getpass.getpass("Adgangskode: ");
        
            #Opret pakke med login-oplysninger.
            packet = Packet00Login(username, password);
            #Afsend pakke til serveren.
            packet.sendData(self.sock);

            #Vent på at ValidationEvent bliver True.
            self.WaitForValidationEvent.wait();
            #Nulstil ValidationEvent til False.
            self.WaitForValidationEvent.clear();
            
            if(self.validated):
                print("Login-oplysninger kunne verificeres.");
            else:
                print("Login-oplysninger kunne ikke verificeres.");

        #Vent på ColorAssignmentEvent
        self.WaitForColorAssignmentEvent.wait();
        if (self.order):
            print("Du er hvid spiller.");
        else:
            print("Du er sort spiller.");

        while (self.running):
            self.board.printChessboard(self.order);
            self.WaitForPacketMoveEvent.wait();

            pos1 = input("Flyt brik fra position: ").upper();
            pos2 = input("Til position: ").upper();
            packet = Packet03Move(pos1, pos2);
            self.board.move(pos1, pos2);
            packet.sendData(self.sock);

            #Nulstul MoveEvent til False.
            self.WaitForPacketMoveEvent.clear();

client = Client(socket.gethostname(), 1505);