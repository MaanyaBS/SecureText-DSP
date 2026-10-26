# SecureText Diagrams

Each diagram is given as Mermaid source (renders on GitHub, VS Code with a Mermaid extension, or https://mermaid.live) and as a pre-rendered PNG in `docs/diagrams/`. The `.mmd` files in that folder are the single source.

## System architecture

![System architecture](diagrams/01_architecture.png)

```mermaid
flowchart TB
    U["User"] --> GUI
    subgraph GUI["GUI layer - gui/main_window.py (Tkinter and ttk)"]
        T1["Dashboard"]
        T2["Key Management"]
        T3["Encryption and Decryption"]
        T4["Digital Signature"]
        T5["Hybrid Encryption"]
        T6["RSA Math and Help"]
    end
    GUI --> UT["Utilities: validation.py, file_handler.py"]
    GUI --> CR
    subgraph CR["Crypto layer - crypto package"]
        K["rsa_keys.py: generate, PEM export and import"]
        E["rsa_encryption.py: RSA-OAEP SHA-256"]
        S["digital_signatures.py: RSA-PSS SHA-256"]
        H["hybrid_encryption.py: AES-256-GCM plus RSA-OAEP"]
        TY["toy_rsa.py: educational textbook RSA"]
    end
    CR --> LIB["Python cryptography library"]
    UT --> FS["Local files: PEM keys, ciphertext, signatures"]
```

## Use-case diagram

![Use-case diagram](diagrams/02_use_case.png)

```mermaid
flowchart LR
    A(["Sender"])
    R(["Recipient"])
    subgraph SYS["SecureText system"]
        U1("Generate RSA key pair")
        U2("Export or import keys")
        U3("Encrypt message with recipient public key")
        U4("Decrypt message with own private key")
        U5("Sign message with own private key")
        U6("Verify signature with signer public key")
        U7("Hybrid encrypt or decrypt long message")
        U8("Run tamper and wrong key demos")
        U9("Study RSA mathematics")
    end
    A --> U1
    A --> U2
    A --> U3
    A --> U5
    A --> U7
    R --> U1
    R --> U2
    R --> U4
    R --> U6
    R --> U7
    A --> U8
    R --> U8
    A --> U9
    R --> U9
```

## Data-flow diagram (level 1)

![Data-flow diagram (level 1)](diagrams/03_dfd.png)

```mermaid
flowchart LR
    USER["External entity: User"]
    P1(["1.0 Manage keys"])
    P2(["2.0 Encrypt and decrypt"])
    P3(["3.0 Sign and verify"])
    P4(["4.0 Hybrid encrypt and decrypt"])
    D1[("D1: Keys in memory and PEM files")]
    D2[("D2: Ciphertext, signature and envelope text")]
    USER -->|"key size, password"| P1
    P1 -->|"key pair, PEM"| D1
    D1 -->|"public key"| P2
    D1 -->|"private key"| P2
    USER -->|"plaintext or ciphertext"| P2
    P2 -->|"Base64 ciphertext or plaintext"| D2
    D1 -->|"private key"| P3
    D1 -->|"public key"| P3
    USER -->|"message, signature"| P3
    P3 -->|"signature or valid or invalid"| D2
    D1 -->|"keys"| P4
    USER -->|"long text or envelope"| P4
    P4 -->|"JSON envelope or plaintext"| D2
    D2 -->|"results shown"| USER
```

## Application flowchart

![Application flowchart](diagrams/04_app_flowchart.png)

```mermaid
flowchart TD
    A(["Start: python main.py"]) --> B{"Tkinter and cryptography available?"}
    B -- No --> B1["Print help message and exit"]
    B -- Yes --> C["Open main window"]
    C --> D{"Key pair loaded?"}
    D -- No --> E["Generate key pair or import private key"]
    E --> F
    D -- Yes --> F{"Choose a tab"}
    F --> G["Encrypt"]
    F --> H["Decrypt"]
    F --> I["Sign"]
    F --> J["Verify"]
    F --> K["Hybrid"]
    G --> G1{"Input valid and within 190 bytes?"}
    G1 -- No --> X["Show clear error"]
    G1 -- Yes --> G2["RSA-OAEP encrypt, show Base64"]
    H --> H1{"Base64 valid and correct key?"}
    H1 -- No --> X
    H1 -- Yes --> H2["Show plaintext"]
    I --> I1["RSA-PSS sign, show Base64"]
    J --> J1{"Signature valid?"}
    J1 -- Yes --> J2["Show VALID"]
    J1 -- No --> J3["Show INVALID"]
    K --> K1["AES-GCM encrypt and RSA wrap, or unwrap and decrypt"]
    X --> F
    G2 --> F
    H2 --> F
    I1 --> F
    J2 --> F
    J3 --> F
    K1 --> F
```

## RSA key-generation process

![RSA key-generation process](diagrams/05_keygen_flow.png)

```mermaid
flowchart TD
    A["Choose key size, minimum 2048 bits"] --> B["Library generates two large random primes p and q"]
    B --> C["n = p x q"]
    C --> D["phi of n = p minus 1 times q minus 1"]
    D --> E["e = 65537, check gcd of e and phi = 1"]
    E --> F["d = e inverse modulo phi"]
    F --> G["Public key = n and e"]
    F --> H["Private key = n and d, with p and q"]
    G --> I["Export as PEM, safe to share"]
    H --> J["Export as PKCS8 PEM encrypted with password"]
```

## RSA-OAEP encryption and decryption sequence

![RSA-OAEP encryption and decryption sequence](diagrams/06_encrypt_sequence.png)

```mermaid
sequenceDiagram
    participant S as Sender
    participant A as SecureText
    participant R as Recipient
    R->>S: Public key PEM
    S->>A: Plaintext, max 190 bytes for 2048 bit key
    A->>A: Check length, encode UTF-8
    A->>A: RSA-OAEP with SHA-256 using public key
    A->>S: Ciphertext in Base64
    S->>R: Send Base64 ciphertext
    R->>A: Paste ciphertext
    A->>A: Base64 decode, RSA-OAEP decrypt with private key
    A->>R: Plaintext, or error if wrong key or modified
```

## RSA-PSS signature sequence

![RSA-PSS signature sequence](diagrams/07_signature_sequence.png)

```mermaid
sequenceDiagram
    participant S as Signer
    participant A as SecureText
    participant V as Verifier
    S->>A: Message
    A->>A: SHA-256 hash and RSA-PSS sign with private key
    A->>S: Signature in Base64
    S->>V: Message and signature, public key shared earlier
    V->>A: Message, signature, signer public key
    A->>A: RSA-PSS verify with SHA-256
    A->>V: VALID, or INVALID if message or key differs
```

## Hybrid encryption workflow

![Hybrid encryption workflow](diagrams/08_hybrid_sequence.png)

```mermaid
sequenceDiagram
    participant S as Sender
    participant A as SecureText
    participant R as Recipient
    S->>A: Long message
    A->>A: Generate fresh random 256 bit AES key
    A->>A: Generate random 12 byte nonce
    A->>A: AES-256-GCM encrypt message, get ciphertext and tag
    A->>A: RSA-OAEP wrap AES key with recipient public key
    A->>S: JSON envelope in Base64: version, alg, wrapped_key, nonce, ciphertext
    S->>R: Send envelope
    R->>A: Envelope
    A->>A: RSA-OAEP unwrap AES key with private key
    A->>A: AES-GCM decrypt and verify tag
    A->>R: Plaintext, or authentication failure if altered
```
