#!/usr/bin/python3

import socket;

class UserConfigManager():
    import hashlib
    import configparser
    import secrets

    def __init__(self):
        #Jeg opretter et nyt ConfigParser-objekt.
        self.config = self.configparser.ConfigParser();
        #Jeg indlæser brugerkonfigurationsfilen.
        self.config.read("USERS.ini");

    def addUser(self, username, password):
        if (not self.userExists(username)):
            salt = self.generateSalt();
            hash = self.generateHash(password, salt);
            self.config[username] = {"hash": hash,
                                     "salt": salt};
            return True;
        return False;

    def deleteUser(self, username):
        if (self.userExists(username)):
            self.config.remove_section(username);
            return True;
        return False;

    def userExists(self, username):
        return self.config.has_section(username);

    def saveConfig(self):
        #Jeg åbner en output-stream til konfigurationsfilen.
        configfile = open('USERS.ini', 'w');
        #Jeg videregiver output-streamen til ConfigParser-objektet, for at gemme dataene.
        self.config.write(configfile);
    
    def verifyCredentials(self, username, password):
        if (self.userExists(username)):
            salt = self.config[username]["salt"];
            hash = self.config[username]["hash"];
            if (self.generateHash(password, salt) == hash):
                return True;
        return False;

    def getUserInformation(self, username):
        if (userExists(username)):
            return self.config[username];

    def generateSalt(self):
        #Jeg erklærer en streng med alle de karakterer, der kan bruges i saltet.
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        salt = [];
        #For-lykken kører 16 gange, for at lave et salt på 16 karakterer.
        for i in range(16):
            salt.append(self.secrets.choice(alphabet));

        return "".join(salt);
    
    def generateHash(self, password, salt):
        return self.hashlib.sha1((password + salt).encode("utf-8")).hexdigest();

class Chessboard():

    columns = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H');

    symbols = ("X", "K", "D", "L", "S", "T", "B");
    colors = ("H", "S");

    def __init__(self):
        self.board = [
                ["ST",  "SS",   "SL",   "SD",   "SK",   "SL",   "SS",   "ST"],
                ["SB",  "SB",   "SB",   "SB",   "SB",   "SB",   "SB",   "SB"],
                ["X",   "X",    "X",    "X",    "X",    "X",    "X",    "X"],
                ["X",   "X",    "X",    "X",    "X",    "X",    "X",    "X"],
                ["X",   "X",    "X",    "X",    "X",    "X",    "X",    "X"],
                ["X",   "X",    "X",    "X",    "X",    "X",    "X",    "X"],
                ["HB",  "HB",   "HB",   "HB",   "HB",   "HB",   "HB",   "HB"],
                ["HT",  "HS",   "HL",   "HD",   "HK",   "HL",   "HS",   "HT"]
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

    def isInsideBoard(self, pos):
        xPos = Chessboard.columns.index(pos[0]) + 1;
        yPos = int(pos[1]);
        if (xPos < 1 or xPos > 8 or yPos > 8 or yPos < 1):
            return False;
        return True;

    @staticmethod
    def rawToPos(rawPos):
        #Når en position sendes over netværket sendes den som et tocifret tal hvoraf ét er x-koordinatet og ét er y-koordinatet.
        #Dette er funktionen, til at omforme den rå data, til samme form som spillerinput.
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
        #Hver anden byte er position og den byte før positionen er brikudseendet.
        
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
            #Packet02AssignColor indeholder en byte for farvetildeling, samt om det er spillerens tur.
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
            #1 for True
            temp = bytes([1]);
        else:
            #0 for False
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
    def __init__(self, board):
        super().__init__(5);
        self.board = board;

    def getData(self):
        return self.packetID + Chessboard.boardToRaw(self.board);

import threading;
class ServerClient(threading.Thread):

    def __init__(self, sock, address, server, color):
        threading.Thread.__init__(self);
        self.sock = sock;
        self.address = address;
        self.server = server;
        self.color = color;
        self.validated = False;
        self.username = "";

    def run(self):
        #Makspakkestørrelse målt i bytes
        size = 128;

        while (not self.validated):
            try:
                data = self.sock.recv(size);
                if (data):
                    packet = Packet.parsePacket(data);

                    if (isinstance(packet, Packet00Login)):
                        username = packet.username;
                        validated = self.server.userConfigManager.verifyCredentials(packet.username, packet.password);
                        packet = Packet01LoginValidation(validated);
                        packet.sendData(self.sock);

                        if (validated):
                            #Send brættets brikker
                            packet = Packet05BoardStatus(self.server.board);
                            packet.sendData(self.sock);

                            #Send pakke omkring validerede login-oplysninger.
                            self.username = username;
                            self.validated = True;

                            #Jeg laver dette tjek lige inden afsending af Packet02AssignColor, da modstanderen kan have flyttet en brik, mens denne loggede ind.
                            #turn skifter mellem True og False, der angiver henholdsvis hvid og sort. 
                            #Hvis turen eksempelvis er sort og farven spilleren får tildelt er sort, skal spilleren også "starte".
                            #Ovenover vil kun ske ved udfald.
                            starting = False;
                            if (self.color == self.server.turn):
                                starting = True;

                            packet = Packet02AssignColor(self.color, starting);
                            packet.sendData(self.sock);
                        else:
                            print("Bruger", username, "fejlede login.");

                else:
                    raise Exception("Client disconnected");
            except Exception as e:
                print(e.args);
                self.closeAndRemove();
                return;


        while (self.server.running):
            try:
                data = self.sock.recv(size);
                if (data):
                    packet = Packet.parsePacket(data);
                    if (isinstance(packet, Packet03Move)):

                        if (self.color != self.server.turn):
                            continue;

                        self.server.board.move(packet.pos1, packet.pos2);
                        self.server.turn = not self.server.turn;

                        opponent = self.server.getOpponent(self);
                        if (opponent != None):
                            if (opponent.validated):
                                #Send først Packet03Move-pakker efter modstander er valideret, da denne alligevel modtager hele skakbrættet ved validering.
                                packet.sendData(opponent.sock);
                    self.server.board.printChessboard(self.color);
                else:
                    raise Exception("Client disconnected");
            except Exception as e:
                print(e.args);
                self.closeAndRemove();
                return;

    def sendPacket(self, packet):
        packet.sendData(self.sock);

    def closeAndRemove(self):
        self.sock.close();
        self.server.removeClient(self);


class Server():
    import socket;
    import threading;
    import getpass

    def __init__(self, host, port):
        self.host = host;
        self.port = port;
        #Opret sokkel
        self.sock = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM);
        self.running = True;
        #Bind IP-adresse og port, så soklen kan bruges som serversokkel, og udefrakommende har noget at forbinde til.
        self.sock.bind((self.host, self.port));
        
        self.userConfigManager = UserConfigManager();
        self.userConfigManager.addUser("Esben", "1234");
        self.userConfigManager.saveConfig();

        #Opret tråd der tager imod kommandoer og starter den.
        self.threading.Thread(target=self.commandListener).start();

        #Tom liste til klienterne.
        self.clients = [];

        self.board = None;

        self.turn = True;


    def listen(self):
        #Lyt efter indkomne klienter. Køen der kan vente på at blive accepteret (.accept()), kan højest nå 2 klienter.
        self.sock.listen(2);
        
        while (self.running):
            (sock, address) = self.sock.accept();

            numberOfClients = len(self.clients);
            if (numberOfClients >= 2):
                sock.close();
            else:
                print("Client", address, "connected.");
                if (numberOfClients == 0):
                    self.board = Chessboard();
                    #Den første spiller der opretter forbindelse, bliver både teldelt farven sort.
                    serverClient = ServerClient(sock, address, self, True);
                    self.addClient(serverClient);
                    serverClient.start();
                elif (numberOfClients == 1):
                    color = not self.clients[0].color;
                    serverClient = ServerClient(sock, address, self, color);
                    self.addClient(serverClient);
                    serverClient.start();

    def commandListener(self):
        while (self.running):
            command = input().upper();
            if (command == "ADD USER"):
                username = input("Brugernavn: ");
                password = self.getpass.getpass("Adgangskode: ");
                if (self.userConfigManager.addUser(username, password)):
                    self.userConfigManager.saveConfig();
                    print("Bruger", username, "oprettet.");
                else:
                    print("Bruger", username, "findes allerede.");
            elif (command == "DELETE USER"):
                username = input("Brugernavn: ");
                if (self.userConfigManager.deleteUser(username)):
                    self.userConfigManager.saveConfig();
                    print("Bruger", username, "slettet.");
                else:
                    print("Bruger", username, "findes ikke.");

    def addClient(self, serverClient):
        self.clients.append(serverClient);

    def removeClient(self, serverClient):
        self.clients.remove(serverClient);

    def getOpponent(self, clientSelf):
        for serverClient in self.clients:
            if (serverClient != clientSelf):
                return serverClient;

    def broadcast(self, packet):
        for serverClient in self.clients:
            packet.sendData(serverClient.sock);


server = Server(socket.gethostname(), 1505);
server.listen();