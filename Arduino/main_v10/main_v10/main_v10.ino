// Programa Principal - Traykson
// V9.0 -
// Giovane e Douglas
// 05/2019


#include <SPI.h>
#include <MFRC522.h>
#include "pitches.h"
#include <PID_v1.h>

boolean comPeso;
int classePeso;

char destino;
int tentativa;

//--------Constantes SRFID--------------------------------------

// Pinos ja definidos pela Bibliotecal
// SPI MOSI    MOSI         51
// SPI MISO    MISO         50
// SPI SCK     SCK          52

#define RST_PIN         48
#define SS_1_PIN        53
#define SS_2_PIN        49

#define NR_OF_READERS   2

byte ssPins[] = {SS_1_PIN, SS_2_PIN};

MFRC522 mfrc522[NR_OF_READERS];   // Create MFRC522 instances.

// Create type rfid_sensors, where cross == 0 and tray == 1, and define srfid as that type
enum rfid_sensors : uint8_t {cross, tray} srfid;


//---------Constante do Buzzer---------------------------------

const int BUZ = 45;

//----------Constantes PID------------------------
//Define Variables we'll be connecting to
double SetpointC, InputC, OutputC;
double SetpointB, InputB, OutputB;

//Specify the links and initial tuning parameters
double Kp = 0.4, Ki = 0.3, Kd = 0.01;
PID myPID_C(&InputC, &OutputC, &SetpointC, Kp, Ki, Kd, DIRECT);
PID myPID_B(&InputB, &OutputB, &SetpointB, Kp, Ki, Kd, DIRECT);



//---------Constantes dos Encoders-----------------------------

int pino_D0 = 20;
int pino_D1 = 21;
float rpmC;
float rpmB;
volatile int pulsosC;
volatile int pulsosB;
unsigned long timeold, timeold_card;
unsigned long time_elaps, time_elaps_card;

const float pulsos_por_volta = 24;

//tempo que recolhemos a amostra  de pulsos p/ calcular velocidade
const unsigned int time_sample = 200;
const unsigned int time_sample_card = 500;

//constante de conversao de pulsos para rmp
const float rpm_const = (double)(60.0 * 1000.0) / (double) (pulsos_por_volta*time_sample);

//---------Constantes dos Motores------------------------------

// motor_A
const int IN1A = 2 ;
const int velocidadeA = 3;
const int IN2A = 4 ;

// motor_B
const int velocidadeB = 5;
const int IN3B = 7;
const int IN4B = 6;

// motor_C
const int velocidadeC = 10;
const int IN1C = 9;
const int IN2C = 8;

// motor D
const int velocidadeD = 11;
const int IN3D = 12;
const int IN4D = 13;

// micro switches
const int swt_bottom = 46;
const int swt_top = 47;

// Variaveis controle por infravermelho
double velocidadeBase;
double vA, vB, vC;
int vfA, vfB, vfC;

//----------Constantes dos S. Infravermelhos------------------
// Sensores infra-vermelho
const int S1_pin_frente = A11;
const int S2_pin_frente = A12;
const int S3_pin_frente = A13;
const int S4_pin_frente = A14;
const int S5_pin_frente = A15;

// Sensores infra-vermelho ré
const int S1_pin_re = A9;
const int S2_pin_re = A8;
const int S3_pin_re = A7;
const int S4_pin_re = A6;
const int S5_pin_re = A5;


byte mfrc522_uid[10] = {0};
byte mfrc522_uid_old[10] = {0};
int S1_frente, S2_frente, S3_frente, S4_frente, S5_frente;
int S1_re, S2_re, S3_re, S4_re, S5_re;
int isS1, isS2, isS3, isS4, isS5;

// Matriz de erros para sensores de linha frontal
double erroP_esquerda[2][2] =
{ {0, -200},
  { -500, 0}
};

double erroP_direita[2][2] =
{ {0, 500},
  {200, 0}
};


// Matriz de erros para sensores de linha traseiro
double erroP_esquerda_re[2][2] =
{ {0, -900},
  { -400, 0}
};

double erroP_direita_re[2][2] =
{ {0, 400},
  {900, 0}
};

double erroP, old_erroP, erroD, erroI;

//----------- Cartoes RFID ------------------------------------

byte cards[][4] = {
  {0xCA, 0x0A, 0xDB, 0x2B}, // cruz1
  {132, 194, 65, 30}, // cruz2
  {0xEA, 0x48, 0x5B, 0x2E}, // cruz3
  {0x83, 0x84, 0x24, 0x2E}, // meio 1
  {131, 48, 73, 46}, // meio 2
  {0x73, 0xDB, 0x95, 0x2E}, // meio 3
  {0x73, 0xE6, 0x99, 0x2E}, // mesa 1
  {115, 151, 118, 46}, // mesa 2
  {0x31, 0x31, 0x67, 0x2E}, // mesa 3
  {131, 80, 140, 46}
}; // cozinha
enum card_tags : uint8_t {cruz1, cruz2, cruz3, meio1, meio2, meio3, mesa1, mesa2, mesa3, cozinha};

// 0 = cozinha, 1 = mesa
int objetivo;


//-------- Funções de Tratamento de Interrupcao dos Encoders---------------------------------
void contadorC()
{
  //Incrementa contador
  pulsosC++;
}

void contadorB()
{
  //Incrementa contador
  pulsosB++;
}

void drop (int pwr);


//---------------------------------Configuracoes---------------------------------------------


void livre() {
  //MA
  digitalWrite(IN1A, LOW);
  digitalWrite(IN2A, LOW);
  //MB
  digitalWrite(IN3B, LOW);
  digitalWrite(IN4B, LOW);
  delay(110);
  //MC
  digitalWrite(IN1C, LOW);
  digitalWrite(IN2C, LOW);
}


void parada() {
  //MA
  digitalWrite(IN1A, HIGH);
  digitalWrite(IN2A, HIGH);
  //MB
  digitalWrite(IN3B, HIGH);
  digitalWrite(IN4B, HIGH);
  //MC
  digitalWrite(IN1C, HIGH);
  digitalWrite(IN2C, HIGH);
}

void giro_horario(int vel) {
  //Sentido horario
  //MA
  digitalWrite(IN1A, LOW);
  digitalWrite(IN2A, HIGH);
  analogWrite(velocidadeA, vel);

  //MC
  digitalWrite(IN1C, LOW);
  digitalWrite(IN2C, HIGH);
  analogWrite(velocidadeC, vel * 0.863);

  //MB
  digitalWrite(IN3B, LOW);
  digitalWrite(IN4B, HIGH);
  analogWrite(velocidadeB, vel);
}


void giro_antihorario(int vel) {
  // Sentido Antihorario
  // MA
  digitalWrite(IN1A, HIGH);
  digitalWrite(IN2A, LOW);
  analogWrite(velocidadeA, vel);

  //MC
  digitalWrite(IN1C, HIGH);
  digitalWrite(IN2C, LOW);
  analogWrite(velocidadeC, vel * 0.863);

  //MB
  digitalWrite(IN3B, HIGH);
  digitalWrite(IN4B, LOW);
  analogWrite(velocidadeB, vel);
}


void atras(int velA, int velB, int velC) {
  //MA livre
  digitalWrite(IN1A, LOW);
  digitalWrite(IN2A, HIGH);
  analogWrite(velocidadeA, velA * 0.95);

  if (velC > 0) {
    //MC horario
    digitalWrite(IN1C, LOW);
    digitalWrite(IN2C, HIGH);
    analogWrite(velocidadeC, velC);
  } else if (velC < 0) {
    //MC antihorario
    digitalWrite(IN1C, HIGH);
    digitalWrite(IN2C, LOW);
    analogWrite(velocidadeC, -velC);
  } else {
    digitalWrite(IN1C, LOW);
    digitalWrite(IN2C, LOW);
    analogWrite(velocidadeC, 0);
  }

  //MB antihorario
  digitalWrite(IN3B, HIGH);
  digitalWrite(IN4B, LOW);
  analogWrite(velocidadeB, velB);
}

void afrente(int velA, int velB, int velC) {

  //MA livre
  digitalWrite(IN1A, HIGH);
  digitalWrite(IN2A, LOW);
  analogWrite(velocidadeA, velA * 0.9);

  //MC antihorario
  digitalWrite(IN1C, LOW);
  digitalWrite(IN2C, LOW);
  analogWrite(velocidadeC, 0);

  //MB horario
  digitalWrite(IN3B, LOW);
  digitalWrite(IN4B, HIGH);
  analogWrite(velocidadeB, (int) velB);
}

int S1isBlack() {
  S1_frente = analogRead(S1_pin_frente);
  return (S1_frente < 200) ? 1 : 0;
}

int S2isBlack() {
  S2_frente = analogRead(S2_pin_frente); 
  return (S2_frente < 200) ? 1 : 0;
}

int S3isBlack() {
  S3_frente = analogRead(S3_pin_frente); 
  return (S3_frente < 200) ? 1 : 0;
}

int S4isBlack() {
  S4_frente = analogRead(S4_pin_frente); 
  return (S4_frente < 200) ? 1 : 0;
}

int S5isBlack() {
  S5_frente = analogRead(S5_pin_frente); 
  return (S5_frente < 200) ? 1 : 0;
}


int S1ReIsBlack() {
  S1_re = analogRead(S1_pin_re);
  return (S1_re < 200) ? 1 : 0;
}

int S2ReIsBlack() {
  S2_re = analogRead(S2_pin_re); 
  return (S2_re < 200) ? 1 : 0;
}

int S3ReIsBlack() {
  S3_re = analogRead(S3_pin_re); 
  return (S3_re < 200) ? 1 : 0;
}

int S4ReIsBlack() {
  S4_re = analogRead(S4_pin_re); 
  return (S4_re < 200) ? 1 : 0;
}

int S5ReIsBlack() {
  S5_re = analogRead(S5_pin_re); 
  return (S5_re < 200) ? 1 : 0;
}


void turn_left() {
  int power = 0;
  if (comPeso) {
    power = 150 + classePeso * 7;
  }
  else power = 150;
  
  while (!S1isBlack()) {    
    giro_antihorario(power);
  }

  while (!S3isBlack()) {    
    giro_antihorario(power);
  }
  
  parada();
  
  timeold = millis();
  timeold_card = millis();
}

void turn_right() {
  int power = 0;

  if (comPeso) {
    power = 150 + classePeso * 7;
  }
  else power = 150;
  
  while (!S5isBlack()) {    
    giro_horario(power);
  }
  
  while (!S3isBlack()) {    
    giro_horario(power);
  }
  
  parada();
  
  timeold = millis();
  timeold_card = millis();
}

void lift (int pwr) {
  while (digitalRead(swt_top) == HIGH) {
    digitalWrite(IN3D, LOW);
    digitalWrite(IN4D, HIGH);
    analogWrite(velocidadeD, pwr);
  }

  analogWrite(velocidadeD, 0);
  digitalWrite(IN3D, LOW);
  digitalWrite(IN4D, LOW);
  delay(500);
}

void drop (int pwr) {
  while (digitalRead(swt_bottom) == HIGH) {
    digitalWrite(IN3D, HIGH);
    digitalWrite(IN4D, LOW);
    analogWrite(velocidadeD, pwr);
  }

  analogWrite(velocidadeD, 0);
  digitalWrite(IN3D, LOW);
  digitalWrite(IN4D, LOW);
  delay(500);
}

void seguir_linha_ate_o_fim() {


  while (S1isBlack() || S2isBlack() || S3isBlack() || S4isBlack() || S5isBlack()) {
    seguir_linha();
  }

  parada();
}

void seguir_linha() {
  //afrente(vfA, vfB, vfC);

  // zerar variaveis
  vA = 0;
  vB = 0;

  erroP = 0;

  erroP = erroP_esquerda[S1isBlack()][S2isBlack()] + erroP_direita[S4isBlack()][S5isBlack()];

  erroD = erroP - old_erroP;
  old_erroP = erroP;

  vA = (1000) - erroP - 0.8 * erroD; // Motor da direita;
  vB = (1000) + erroP + 0.8 * erroD; // Motor da esquerda


  vA = vA * velocidadeBase / (1300 - classePeso * 10);
  vB = vB * velocidadeBase / (1300 - classePeso * 10);

  //  Serial.print("ErroP: ");
  //  Serial.print(erroP);
  //  Serial.print(" :: ");
  //  Serial.print(vA);
  //  Serial.print(" :: ");
  //  Serial.println(vB);

  if (vA > 255) vA = 255;
  if (vB > 255) vB = 255;

  if (vA < 0) vA = 0;
  if (vB < 0) vB = 0;

  vfA = round(vA);
  vfB = round(vB);
  vfC = 0;
  afrente(vfA, vfB, vfC);
}


void seguir_linha_re() {
  //atras(vfA, vfB, vfC);

  // zerar variaveis
  vA = 0;
  vB = 0;
  vC = 0;

  erroP = 0;

  erroP = erroP_esquerda_re[S1ReIsBlack()][S2ReIsBlack()] + erroP_direita_re[S4ReIsBlack()][S5ReIsBlack()];

  erroD = erroP - old_erroP;
  old_erroP = erroP;

  vA = (1000) + erroP + 0.8 * erroD; // Motor da direita;
  vB = (1000) - erroP - 0.8 * erroD; // Motor da esquerda
  
  vA = vA * velocidadeBase / (1300 - classePeso * 10);
  vB = vB * velocidadeBase / (1300 - classePeso * 10);

  double baseC;
  if(erroP < 0)  baseC = -80.0;
  if(erroP == 0) baseC = 0.0;
  if(erroP > 0)  baseC = 80.0;
  vC = (erroP / 20.0 + baseC) + (0.8 * erroD);

  if (vA > 255) vA = 255;
  if (vB > 255) vB = 255;
  
  if (vA < 0) vA = 0;
  if (vB < 0) vB = 0;

  vfA = round(vA);
  vfB = round(vB);
  vfC = round(vC);
  atras(vfA, vfB, vfC);
}

void recolher_bandeja() {
  seguir_linha_ate_o_fim();
  parada();
  delay(1000);
  if (temCartao(tray)) {
    // if (true) {
    lift(250);
    comPeso = true;
    Serial.print('S');
    play_tone(NOTE_C5);
    while (!(IDsIguais(mfrc522_uid, cards[meio1]) || IDsIguais(mfrc522_uid, cards[meio2]) || IDsIguais(mfrc522_uid, cards[meio3]))
           &&
           (!(IDsIguais(mfrc522_uid, cards[cruz1]) || IDsIguais(mfrc522_uid, cards[cruz2]) || IDsIguais(mfrc522_uid, cards[cruz3])))) {
      temCartao(cross);
      seguir_linha_re();
    }
    parada();
    turn_left();
    drop(80);
    tentativa = 0;
    objetivo = 1;
  } else {
    while (!(IDsIguais(mfrc522_uid, cards[meio1]) || IDsIguais(mfrc522_uid, cards[meio2]) || IDsIguais(mfrc522_uid, cards[meio3]))
           &&
           (!(IDsIguais(mfrc522_uid, cards[cruz1]) || IDsIguais(mfrc522_uid, cards[cruz2]) || IDsIguais(mfrc522_uid, cards[cruz3])))) {
      temCartao(cross);
      seguir_linha_re();
    }

    if (tentativa < 1) {
      while (!(IDsIguais(mfrc522_uid, cards[mesa1]) || IDsIguais(mfrc522_uid, cards[mesa2]) || IDsIguais(mfrc522_uid, cards[mesa3]))) {
        temCartao(cross);
        seguir_linha();
      }
      // parada();
      tentativa++;
      recolher_bandeja();
    } else {
      Serial.print('N');
      classePeso = 0;
      tentativa = 0;
      turn_right();
      objetivo = 1;
      play_tone(NOTE_C3);
    }
  }
}

int IDsIguais(byte * rfid_1, byte * rfid_2) {
  if (
    rfid_1[0] == rfid_2[0] &&
    rfid_1[1] == rfid_2[1] &&
    rfid_1[2] == rfid_2[2] &&
    rfid_1[3] == rfid_2[3]) {
    return 1;
  } else {
    return 0;
  }
  return 0;
}

void aproximar() {
  char cancelar = ' ';
  while (objetivo == 0) {
    if (temCartao(cross) && !IDsIguais(mfrc522_uid, mfrc522_uid_old)) {
      livre();
      if (IDsIguais(mfrc522_uid, cards[meio1]) || IDsIguais(mfrc522_uid, cards[meio2]) || IDsIguais(mfrc522_uid, cards[meio3])) {
        if (objetivo == 0) {
          parada();
          Serial.print('A');
          delay(1000); // TO DO gritar()
          for (int i = 0; i < 7; i++)
          {
            play_tone();
            delay(500);
          }

          Serial.print(destino);
          while (!Serial.available());

          cancelar = Serial.read();
          if (cancelar == '0') {
            Serial.print('0');
            objetivo = 1;
            turn_left();
            while (!temCartao(cross)
                   ||
                   (!(IDsIguais(mfrc522_uid, cards[cruz1]) || IDsIguais(mfrc522_uid, cards[cruz2]) || IDsIguais(mfrc522_uid, cards[cruz3])))) {
              seguir_linha();
            }
            turn_left();
          } else if (cancelar == 'B') {
            classePeso = 3;
            play_tone(NOTE_E3);
            Serial.print('B');
          } else if (cancelar == 'H') {
            classePeso = 3;
            play_tone(NOTE_E3);
            Serial.print('B');
          } else if (cancelar == 'M') {
            classePeso = 2;
            play_tone(NOTE_E3);
            Serial.print('B');
          } else if (cancelar == 'L') {
            classePeso = 1;
            play_tone(NOTE_E3);
            Serial.print('B');
          } else {
            while (1) {
              play_tone(NOTE_E3);
              delay(200);
            }
          }

        } else if (objetivo == 1) {
          Serial.print('W');
          turn_left();
        } else {
          Serial.print('X');
        }
      } else if (IDsIguais(mfrc522_uid, cards[mesa1]) || IDsIguais(mfrc522_uid, cards[mesa2]) || IDsIguais(mfrc522_uid, cards[mesa3])) {
        if (objetivo == 0) {
          recolher_bandeja();
          while (!temCartao(cross)
                 ||
                 (!(IDsIguais(mfrc522_uid, cards[cruz1]) || IDsIguais(mfrc522_uid, cards[cruz2]) || IDsIguais(mfrc522_uid, cards[cruz3])))) {
            seguir_linha();
          }
          turn_left();
        } else {

        }
      }

    } else {      
      seguir_linha();
      
    }
  }
}


/***************************************Funcao Check Encoders**********************
    Verifica quantos pulsos foram registrados, calcula e imprime a RPM de cada roda (B e C)
*/
void check_encoders()
{

  time_elaps = millis() - timeold;

  if (time_elaps >= time_sample)
  {
    //Desabilita interrupcao durante o calculo
    detachInterrupt(digitalPinToInterrupt(pino_D0));
    detachInterrupt(digitalPinToInterrupt(pino_D1));


    rpmC = rpm_const * pulsosC;
    rpmB = rpm_const * pulsosB;

    InputC = rpmC;
    InputB = rpmB;

    int SetPoint = 110;

    // Influencia dos infravermelhos sobre a entrada do PID
    SetpointC = SetPoint + vfC;
    SetpointB = SetPoint + vfB;

    // computa apenas quando time_elaps >= SetSampleTime() (=200ms)
    myPID_C.Compute();
    myPID_B.Compute();

    //Mostra o valor de RPM no serial monitor
    //    Serial.print("RPM_C = ");
    //    Serial.print(rpmC, DEC);
    //    Serial.print("   RPM_B = ");
    //    Serial.println(rpmB, DEC);
    //
    //    Serial.print("OutputC = ");
    //    Serial.print(OutputC, DEC);
    //    Serial.print("    OutputB = ");
    //    Serial.println(OutputB, DEC);

    analogWrite(velocidadeA, (int) OutputC);
    analogWrite(velocidadeB, (int) OutputB);


    pulsosC = 0;
    pulsosB = 0;
    timeold = millis();


    attachInterrupt(digitalPinToInterrupt(pino_D0), contadorC, FALLING);
    attachInterrupt(digitalPinToInterrupt(pino_D1), contadorB, FALLING);
  }
}


//-------------Funcao Play Tone no Buzzer-------------------------------
void play_tone() {
  tone(BUZ, NOTE_G3, 300);
}

void play_tone(int tom) {
  tone(BUZ, tom, 300);
}

void play_long_tone() {
  for (int i = 0; i < 30; i++) {
    tone(BUZ, random(30, 2000), 10);
  }
}

/*************************Funcao Check Card*******************************
    Checa se tem uma tag no sensor e imprime na Porta Serial o ID dela
    Argumento "reader": sensor que se deseja ler {cross, tray}
    Retorno: void
*/
int temCartao(uint8_t reader) {

  time_elaps_card = millis() - timeold_card;

  if (time_elaps_card >= time_sample_card) {

    if (mfrc522[reader].PICC_IsNewCardPresent() && mfrc522[reader].PICC_ReadCardSerial()) {

      // Serial.print(F("Reader "));
      // Serial.print(reader);

      // Show some details of the PICC (that is: the tag/card)
      // Serial.print(F(": Card UID: "));

      if (!IDsIguais(mfrc522_uid, mfrc522_uid_old)) {
        mfrc522_uid_old[0] = mfrc522_uid[0];
        mfrc522_uid_old[1] = mfrc522_uid[1];
        mfrc522_uid_old[2] = mfrc522_uid[2];
        mfrc522_uid_old[3] = mfrc522_uid[3];
      }

      if (mfrc522[reader].uid.size == 4)
      {
        dump_byte_array(mfrc522[reader].uid.uidByte, mfrc522[reader].uid.size);
        mfrc522_uid[0] = mfrc522[reader].uid.uidByte[0];
        mfrc522_uid[1] = mfrc522[reader].uid.uidByte[1];
        mfrc522_uid[2] = mfrc522[reader].uid.uidByte[2];
        mfrc522_uid[3] = mfrc522[reader].uid.uidByte[3];
      }

      // Serial.println();

      // Halt PICC
      mfrc522[reader].PICC_HaltA();
      // Stop encryption on PCD
      mfrc522[reader].PCD_StopCrypto1();

      play_tone();

      timeold_card = millis();
      return 1;
    }
  }
  return 0;
}


/**********************Funcao Dump Byte Array***********************
   Transforma um vetor de bytes em hexa e imprime na Porta Serial
   Utilizado na leitura das tags RFIDs
   Argumentos: *buffer - vetor com id da tag em bytes;
                bufferSize - tamanho do vetor de bytes
   Retorno: void
*/
void dump_byte_array(byte * buffer, byte bufferSize) {

  // char array para armazenar o uid como string
  // tamanho: temos 4 bytes no buffer, cada um vira 2 caracteres em hex
  // somamos 3 caracteres de espaco + o caracter nullo de fim de string \0
  char output[(bufferSize * 2) + (bufferSize - 1) + 1];

  // pointer to the first item (0 index) of the output array */
  char *ptr = &output[0];

  for (byte i = 0; i < bufferSize; i++) {

    //to not place space in the begining of the string
    if (i > 0)
      ptr += sprintf (ptr, " ") ;

    //does the conversion and adds 2 to the pointer
    ptr += sprintf (ptr, "%02X", buffer[i]);

  }

  // Serial.print(output);
}

void setup()
{

  Serial.begin(9600);
  while (!Serial);    // Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)


  //--------Configuracao Buzzer------------------------

  pinMode(BUZ, OUTPUT);

  //--------Configuracao SRFID-------------------------

  SPI.begin();        // Init SPI bus

  delay(250);

  for (uint8_t reader = 0; reader < NR_OF_READERS; reader++)
  {
    mfrc522[reader].PCD_Init(ssPins[reader], RST_PIN); // Init each MFRC522 card
    // Serial.print(F("Reader "));
    // Serial.print(reader);
    // Serial.print(F(": "));
    // mfrc522[reader].PCD_DumpVersionToSerial();
  }

  delay(250);
  //--------Configuracao Encoders----------------------
  //Pino do sensor como entrada
  pinMode(pino_D0, INPUT);
  pinMode(pino_D1, INPUT);

  //Aciona o contador a cada pulso
  attachInterrupt(digitalPinToInterrupt(pino_D0), contadorC, FALLING);
  attachInterrupt(digitalPinToInterrupt(pino_D1), contadorB, FALLING);

  //Variaveis
  pulsosC = 0;
  pulsosB = 0;
  rpmB = 0;
  rpmC = 0;
  timeold = 0;
  time_elaps = 0;

  comPeso = false;
  classePeso = 0;
  tentativa = 0;
  velocidadeBase = 265;

  //--------Configuracao Motores----------------------
  pinMode(IN1A, OUTPUT);
  pinMode(IN2A, OUTPUT);
  pinMode(IN3B, OUTPUT);
  pinMode(IN4B, OUTPUT);
  pinMode(IN1C, OUTPUT);
  pinMode(IN2C, OUTPUT);
  pinMode(IN3D, OUTPUT);
  pinMode(IN4D, OUTPUT);

  pinMode(velocidadeA, OUTPUT);
  pinMode(velocidadeB, OUTPUT);
  pinMode(velocidadeC, OUTPUT);
  pinMode(velocidadeD, OUTPUT);

  pinMode(swt_bottom, INPUT_PULLUP);
  pinMode(swt_top, INPUT_PULLUP);

  //------Configuração Infravermelho--------------------------
  pinMode(S1_pin_frente, INPUT);
  pinMode(S2_pin_frente, INPUT);
  pinMode(S3_pin_frente, INPUT);
  pinMode(S4_pin_frente, INPUT);
  pinMode(S5_pin_frente, INPUT);

  //------Configuração Infravermelho Ré-----------------------
  pinMode(S1_pin_re, INPUT);
  pinMode(S2_pin_re, INPUT);
  pinMode(S3_pin_re, INPUT);
  pinMode(S4_pin_re, INPUT);
  pinMode(S5_pin_re, INPUT);

  //--------Configuracao PID--------------------------

  //initialize the variables we're linked to
  InputC = rpmC;
  SetpointC = 125;
  myPID_C.SetOutputLimits(95, 250);

  InputB = rpmB;
  SetpointB = 125;
  myPID_B.SetOutputLimits(95, 250);

  //turn the PID on
  myPID_C.SetMode(AUTOMATIC);
  myPID_B.SetMode(AUTOMATIC);

  digitalWrite(IN3B, HIGH);
  digitalWrite(IN4B, LOW);
  digitalWrite(IN1C, LOW);
  digitalWrite(IN2C, HIGH);
  //analogWrite(velocidadeC, (int) 100);

  old_erroP = 0;
  erroI = 0;
  erroD = 0;

  //------------------- bla ---
  // inicia tentando chegar aa mesa
  objetivo = 0; // 0 = tente chegar na mesa

  if (!comPeso && digitalRead(swt_bottom) == HIGH) {
    drop(80);
  }

  while (!temCartao(tray));
}

//-----------------------------------------MAIN---------------------------------------------
void loop() {

  // Envia para a base que o robô está na cozinha
  Serial.print('K');

  // Aguarda comando da base via bluetooth
  while (!Serial.available()) { // verifica se existem bytes a serem lidos da porta serial
    // nada
  }

  // Recebe comando via bluetooth informando em qual lugar buscar a bandeja
  // destino:
  // 0 = cozinha
  // 1 = lugar 1
  // 2 = lugar 2 etc.
  destino = Serial.read(); // Lê 1 byte da porta serial

  if (destino != '0' && destino != 'T') {
    Serial.print(destino); // Ecoa o dado lido para confirmar recebimento

    livre();
    switch (destino) {      

      case '1':
        while (!temCartao(cross) || !IDsIguais(mfrc522_uid, cards[cruz1])) {
          seguir_linha();
        }
        turn_right();
        aproximar();
        break;

      case '2':
        while (!temCartao(cross) || !IDsIguais(mfrc522_uid, cards[cruz2])) {
          seguir_linha();
        }
        turn_right();
        aproximar();
        break;

      case '3':
        while (!temCartao(cross) || !IDsIguais(mfrc522_uid, cards[cruz3])) {
          seguir_linha();
        }
        turn_right();
        aproximar();
        break;

      default:
        break;
    }

    while ((!temCartao(cross) || !IDsIguais(mfrc522_uid, cards[cozinha]))) {
      seguir_linha();
    }

    livre();
    if (comPeso) {
      while (digitalRead(swt_top) == HIGH) {
        play_tone();
        delay(500);
      }
      play_tone(330);
      delay(2000);
    }

    turn_left();
    comPeso = false;
    classePeso = 0;
    objetivo = 0;
    Serial.print('K');
  }

  if (destino == 'T') {
    while ((!temCartao(cross) || !IDsIguais(mfrc522_uid, cards[cozinha])));
    Serial.print('K');
  }
}
