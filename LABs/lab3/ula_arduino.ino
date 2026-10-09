/*
 * EP03 - ULA 4 bits + Arduino
 *
 * Memoria: vetor de 100 posicoes
 *   mem[0]=PC  mem[1]=W  mem[2]=X  mem[3]=Y  mem[4..99]=programa (instrucoes "XYS")
 * Posicao vazia = -1. Cada instrucao e guardada como numero de 12 bits (ex.: C6B = 0xC6B).
 *
 * Fluxo:
 *   1) CARGA: cole todo o testeula.hex no campo "Enviar" do Monitor Serial (9600 baud).
 *      So carrega no vetor, NAO executa. Erros sao mostrados e a carga continua.
 *   2) Pergunta "Executar programa? (s/n)".
 *   3) EXECUCAO: busca (usa PC) -> decodifica -> executa -> grava W,X,Y,PC -> LEDs -> DUMP.
 *      Intervalo de 4 s entre instrucoes.
 */

const int LED_PINS[4] = {13, 12, 11, 10};      // F3, F2, F1, F0
const int TAM_MEM = 100;                       // tamanho total da memoria
const int INICIO_PROG = 4;                     // primeira posicao do programa
const unsigned long INTERVALO_MS = 4000;       // pausa entre instrucoes
const unsigned long TIMEOUT_CARGA_MS = 1000;   // silencio na serial = fim da carga

int16_t mem[TAM_MEM];                          // memoria + registradores
int prox;                                      // proxima posicao livre do programa
int nErros;                                    // Contador de erros de sintaxe durante a carga

enum Estado { CARGA, PERGUNTA };
Estado estado = CARGA;

bool recebendo = false;                        // chegou algo na carga atual?
bool memSuja = false;                          // memoria ja foi usada (limpar na nova carga)
unsigned long ultimoByte = 0;

char grupo[4];                                 // digitos hex da instrucao em montagem
byte ng = 0;                                   // quantos digitos ja chegaram
bool tokenRuim = false;                        // token atual invalido (ignora o resto)

// Limpa memoria e registradores; apaga LEDs
void iniciarMemoria() {
  for (int i = 0; i < TAM_MEM; i++) mem[i] = -1;
  mem[0] = INICIO_PROG;                        // PC = 4
  mem[1] = 0; mem[2] = 0; mem[3] = 0;          // 0
  prox = INICIO_PROG;
  nErros = 0; ng = 0; tokenRuim = false;
  memSuja = false;
  mostraLeds(0);
}

// Mostra W nos LEDs (bit mais significativo no pino 13)
void mostraLeds(byte w) {
  for (int i = 0; i < 4; i++) digitalWrite(LED_PINS[i], (w >> (3 - i)) & 1);
}

// ULA: A=X, B=Y, S=instrucao (Figura 2). Resultado com 4 bits.
byte ula(byte s, byte a, byte b) {
  byte r = 0;
  switch (s) {
    case 0x0: r = ~a;        break;  // nA
    case 0x1: r = ~(a | b);  break;  // AoBn
    case 0x2: r = ~a & b;    break;  // nAeB
    case 0x3: r = 0;         break;  // zeroL
    case 0x4: r = ~(a & b);  break;  // AeBn
    case 0x5: r = ~b;        break;  // nB
    case 0x6: r = a ^ b;     break;  // AxB
    case 0x7: r = a & ~b;    break;  // AenB
    case 0x8: r = ~a | b;    break;  // nAoB
    case 0x9: r = ~(a ^ b);  break;  // AxBn
    case 0xA: r = b;         break;  // copiaB
    case 0xB: r = a & b;     break;  // AeB
    case 0xC: r = 1;       break;  // umL
    case 0xD: r = a | ~b;    break;  // AonB
    case 0xE: r = a | b;     break;  // AoB
    case 0xF: r = a;         break;  // copiaA
  }
  return r & 0x0F;
}

// Imprime instrucao com 3 digitos hex (ex.: 0x03 -> "003")
void printHex3(int16_t v) {
  if (v < 0x100) Serial.print('0');
  if (v < 0x10) Serial.print('0');
  Serial.print(v, HEX);
}

// DUMP: so ate onde ha instrucoes. PC em decimal; W, X, Y em hex.
void dump() {
  Serial.print(F("->|"));
  
  // Imprime PC
  Serial.print(mem[0]);
  Serial.print(F("|"));

  // Imprime W, X, Y (se ainda forem -1, imprime espaço em branco)
  for (int i = 1; i <= 3; i++) {
    if (mem[i] == -1) {
      Serial.print(F(" |"));
    } else {
      Serial.print(mem[i], HEX);
      Serial.print(F("|"));
    }
  }

  // Imprime as instrucoes carregadas no programa
  for (int i = INICIO_PROG; i < prox; i++) {
    printHex3(mem[i]);
    Serial.print(F("|"));
  }
  Serial.println();
}

// Guarda uma instrucao valida (3 digitos hex) na proxima posicao livre
void armazena(const char *txt) {
  if (prox >= TAM_MEM) {
    nErros++;
    Serial.println(F("ERRO: memoria cheia, instrucao ignorada"));
    return;
  }
  mem[prox++] = (int16_t)strtol(txt, NULL, 16);
}

// Fecha o token atual (chamado em espaco/quebra de linha)
void fechaToken() {
  if (ng > 0) {                                // sobraram digitos: instrucao incompleta
    grupo[ng] = 0;
    nErros++;
    Serial.print(F("ERRO: instrucao incompleta '"));
    Serial.print(grupo);
    Serial.println(F("' (use 3 digitos hex)"));
    ng = 0;
  }
  tokenRuim = false;
}

// Processa um caractere recebido na carga (aceita 1 instrucao por linha ou tudo junto)
void processaChar(char c) {
  if (c == ' ' || c == '\n' || c == '\r' || c == '\t' || c == ',') { fechaToken(); return; }
  if (tokenRuim) return;                       // ignora resto do token invalido
  if (!isHexadecimalDigit(c)) {
    nErros++;
    Serial.print(F("ERRO: caractere invalido '"));
    Serial.print(c);
    Serial.println(F("' - ignorado"));
    tokenRuim = true;
    ng = 0;
    return;
  }
  grupo[ng++] = c;
  if (ng == 3) { grupo[3] = 0; armazena(grupo); ng = 0; }
}

// Fim da carga: mostra o vetor e pergunta se executa
void finalizaCarga() {
  fechaToken();
  recebendo = false;
  if (prox == INICIO_PROG) {
    Serial.println(F("Nenhuma instrucao valida recebida. Envie novamente."));
    return;
  }
  mem[0] = INICIO_PROG;                        // PC aponta para a 1a instrucao
  Serial.print(F("Carga concluida: "));
  Serial.print(prox - INICIO_PROG);
  Serial.print(F(" instrucao(oes), "));
  Serial.print(nErros);
  Serial.println(F(" erro(s)."));
  Serial.println(F("Carga do vetor:"));
  dump();
  Serial.println(F("Executar programa? (s/n)"));
  estado = PERGUNTA;
}

// Existe instrucao na posicao indicada pelo PC?
bool temInstrucao() {
  return mem[0] < TAM_MEM && mem[mem[0]] != -1;
}

// Ciclo: buscar -> decodificar -> executar (Figura 5)
void executar() {
  Serial.println(F("--- Execucao ---"));
  while (temInstrucao()) {
    int pc = mem[0];
    int16_t instr = mem[pc];                   // BUSCA: indexa pelo PC

    byte x = (instr >> 8) & 0xF;               // DECODIFICA XXXX YYYY SSSS
    byte y = (instr >> 4) & 0xF;
    byte s = instr & 0xF;

    byte w = ula(s, x, y);                     // EXECUTA

    mem[1] = w; mem[2] = x; mem[3] = y;        // atualiza W, X, Y
    mem[0] = pc + 1;                           // PC -> proxima instrucao
    mostraLeds(w);
    dump();
    if (temInstrucao()) delay(INTERVALO_MS);
  }
  Serial.println(F("=== Execucao finalizada ==="));
  memSuja = true;                              // proxima carga limpa a memoria
  while (Serial.available()) Serial.read();    // descarta sobras (ex.: '\n')
  estado = CARGA;
}

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < 4; i++) pinMode(LED_PINS[i], OUTPUT);
  iniciarMemoria();
  Serial.println(F("ULA 4 bits pronta. Cole o conteudo do testeula.hex e envie."));
}

void loop() {
  if (estado == CARGA) {
    while (Serial.available()) {
      char c = Serial.read();
      bool branco = (c == ' ' || c == '\n' || c == '\r' || c == '\t');
      if (!recebendo && !branco) {             // primeiro caractere util da carga
        recebendo = true;
        if (memSuja) iniciarMemoria();
      }
      if (recebendo) { ultimoByte = millis(); processaChar(c); }
    }
    if (recebendo && millis() - ultimoByte > TIMEOUT_CARGA_MS) finalizaCarga();
  } else {                                     // PERGUNTA
    while (Serial.available()) {
      char c = Serial.read();
      if (c == 's' || c == 'S') { executar(); break; }
      if (c == 'n' || c == 'N') {
        Serial.println(F("Execucao cancelada. Envie novo programa."));
        iniciarMemoria();
        estado = CARGA;
        break;
      }
    }
  }
}
