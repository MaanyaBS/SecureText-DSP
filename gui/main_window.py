"""SecureText main window (Tkinter / ttk).

All cryptography is delegated to the ``crypto`` package; this module only wires
widgets to those functions and reports results or errors to the user.
Private-key material and passwords are never printed or logged.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from crypto import digital_signatures as sigs
from crypto import hybrid_encryption as hybrid
from crypto import rsa_encryption as enc
from crypto import rsa_keys
from crypto.toy_rsa import ToyRSAError, toy_rsa_walkthrough
from gui.content import ABOUT_TEXT, HELP_TEXT, MATH_TEXT
from utils import file_handler
from utils.validation import ValidationError, require_password

NAVY = "#1F3A5F"
BLUE = "#2E86AB"
BG = "#F4F6F8"
CARD = "#FFFFFF"
OK = "#1B7F3B"
BAD = "#B3261E"
MUTED = "#5F6B7A"

TAB_NAMES = [
    "Dashboard", "Key Management", "Encryption", "Decryption",
    "Digital Signature", "Hybrid Encryption", "RSA Math", "About & Help",
]


class SecureTextApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SecureText - RSA Secure Messaging")
        self.geometry("1020x740")
        self.minsize(900, 640)
        self.configure(bg=BG)

        self.private_key = None      # own RSA private key (memory only)
        self.recipient_pub = None    # imported public key, optional
        self.status_var = tk.StringVar(value="Ready. Generate or import a key pair to begin.")

        self._style()
        self._header()
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 4))
        self._build_dashboard()
        self._build_keys()
        self._build_encrypt()
        self._build_decrypt()
        self._build_signature()
        self._build_hybrid()
        self._build_math()
        self._build_help()
        self._statusbar()
        self.refresh_key_state()

    # ------------------------------------------------------------------ layout
    def _style(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("TFrame", background=BG)
        s.configure("Card.TFrame", background=CARD)
        s.configure("TLabel", background=BG, foreground="#1B2430", font=("Segoe UI", 10))
        s.configure("Card.TLabel", background=CARD)
        s.configure("Title.TLabel", font=("Segoe UI", 15, "bold"), foreground=NAVY)
        s.configure("Muted.TLabel", foreground=MUTED)
        s.configure("TButton", font=("Segoe UI", 10), padding=6)
        s.configure("Accent.TButton", background=BLUE, foreground="white", font=("Segoe UI", 10, "bold"))
        s.map("Accent.TButton", background=[("active", NAVY)])
        s.configure("Danger.TButton", foreground=BAD)
        s.configure("TNotebook", background=BG)
        s.configure("TNotebook.Tab", padding=(12, 6), font=("Segoe UI", 10))
        s.map("TNotebook.Tab", background=[("selected", CARD)], foreground=[("selected", NAVY)])
        s.configure("TLabelframe", background=BG)
        s.configure("TLabelframe.Label", background=BG, foreground=NAVY, font=("Segoe UI", 10, "bold"))

    def _header(self):
        bar = tk.Frame(self, bg=NAVY)
        bar.pack(fill="x")
        tk.Label(bar, text="SecureText", bg=NAVY, fg="white",
                 font=("Segoe UI", 18, "bold")).pack(side="left", padx=14, pady=8)
        tk.Label(bar, text="RSA-OAEP  |  RSA-PSS  |  AES-GCM Hybrid", bg=NAVY, fg="#BFD7EA",
                 font=("Segoe UI", 10)).pack(side="left")

    def _statusbar(self):
        self.status_label = tk.Label(self, textvariable=self.status_var, anchor="w",
                                     bg="#E3E8EE", fg="#1B2430", font=("Segoe UI", 9), padx=10, pady=4)
        self.status_label.pack(fill="x", side="bottom")

    def _tab(self, title, heading, blurb):
        frame = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(frame, text=title)
        ttk.Label(frame, text=heading, style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text=blurb, style="Muted.TLabel", wraplength=940, justify="left").pack(
            anchor="w", pady=(2, 10))
        return frame

    @staticmethod
    def _text(parent, height=6, readonly=False, wrap="word"):
        box = ttk.Frame(parent)
        widget = tk.Text(box, height=height, wrap=wrap, font=("Consolas", 10), relief="solid", bd=1,
                         undo=True)
        bar = ttk.Scrollbar(box, orient="vertical", command=widget.yview)
        widget.configure(yscrollcommand=bar.set)
        widget.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")
        widget.readonly = readonly
        if readonly:
            widget.configure(state="disabled", bg="#EEF1F5")
        return box, widget

    @staticmethod
    def set_text(widget, value):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", value)
        if getattr(widget, "readonly", False):
            widget.configure(state="disabled")

    @staticmethod
    def get_text(widget):
        return widget.get("1.0", "end-1c")

    def _result_label(self, parent):
        label = ttk.Label(parent, text="", wraplength=940, justify="left", font=("Segoe UI", 10, "bold"))
        label.pack(anchor="w", pady=(6, 0))
        return label

    def report(self, label, message, ok=True):
        label.configure(text=message, foreground=OK if ok else BAD)
        self.set_status(message, ok)

    def set_status(self, message, ok=True):
        self.status_var.set(message)
        self.status_label.configure(fg=OK if ok else BAD)

    def _button_row(self, parent, buttons):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=6)
        for text, command, style in buttons:
            ttk.Button(row, text=text, command=command, style=style).pack(side="left", padx=(0, 8))
        return row

    # --------------------------------------------------------------- key state
    @property
    def own_public(self):
        return self.private_key.public_key() if self.private_key else None

    @property
    def effective_public(self):
        """Key used for encrypting and for verifying signatures."""
        return self.recipient_pub or self.own_public

    def refresh_key_state(self):
        if self.private_key:
            pub = self.own_public
            own = (f"Own key pair loaded: {pub.key_size}-bit RSA\n"
                   f"Fingerprint (SHA-256): {rsa_keys.fingerprint(pub)}")
        else:
            own = "No own key pair loaded. Generate one or import a private key."
        if self.recipient_pub:
            rec = ("Recipient / verifier key: IMPORTED public key\n"
                   f"Fingerprint: {rsa_keys.fingerprint(self.recipient_pub)}")
        elif self.private_key:
            rec = "Recipient / verifier key: your own public key (self-test mode)"
        else:
            rec = "Recipient / verifier key: none"
        info = own + "\n" + rec
        self.dash_info.configure(text=info)
        self.key_info.configure(text=info)
        self.enc_key_label.configure(text=rec.replace("Recipient / verifier key", "Encrypting with"))
        self.sig_key_label.configure(text=rec.replace("Recipient / verifier key", "Verifying with"))
        self.hyb_key_label.configure(text=rec.replace("Recipient / verifier key", "Encrypting with"))
        if self.private_key:
            self.set_text(self.pub_text, rsa_keys.export_public_key_pem(self.own_public).decode())
        else:
            self.set_text(self.pub_text, "")

    def _need_private(self):
        if not self.private_key:
            self.set_status("No private key loaded. Generate or import a key pair first.", False)
            messagebox.showwarning("No private key", "Generate a key pair or import a private key first.")
            return False
        return True

    def _need_public(self):
        if not self.effective_public:
            self.set_status("No public key available. Generate a key pair or import a public key.", False)
            messagebox.showwarning("No public key", "Generate a key pair or import a public key first.")
            return False
        return True

    # --------------------------------------------------------------- dashboard
    def _build_dashboard(self):
        f = self._tab("Dashboard", "Welcome to SecureText",
                      "A secure message system built on RSA public-key cryptography. "
                      "Everything runs offline on your computer; keys are kept in memory unless you export them.")
        card = ttk.Frame(f, style="Card.TFrame", padding=14)
        card.pack(fill="x")
        ttk.Label(card, text="Key status", style="Card.TLabel", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.dash_info = ttk.Label(card, text="", style="Card.TLabel", justify="left", wraplength=900)
        self.dash_info.pack(anchor="w", pady=6)

        ttk.Label(f, text="Quick actions", style="Title.TLabel").pack(anchor="w", pady=(16, 6))
        self._button_row(f, [
            ("1. Generate keys", lambda: (self.notebook.select(1), self.generate_keys()), "Accent.TButton"),
            ("2. Encrypt a message", lambda: self.notebook.select(2), "TButton"),
            ("3. Decrypt a message", lambda: self.notebook.select(3), "TButton"),
        ])
        self._button_row(f, [
            ("4. Sign / verify", lambda: self.notebook.select(4), "TButton"),
            ("5. Hybrid (long text)", lambda: self.notebook.select(5), "TButton"),
            ("6. Learn RSA maths", lambda: self.notebook.select(6), "TButton"),
        ])
        summary = ttk.LabelFrame(f, text="What each tab demonstrates", padding=10)
        summary.pack(fill="x", pady=14)
        for line in (
            "Confidentiality  -  RSA-OAEP / AES-GCM hide the message from everyone without the private key.",
            "Integrity  -  any change to a signed or AES-GCM-protected message is detected.",
            "Authenticity  -  an RSA-PSS signature proves the holder of the private key signed the message.",
        ):
            ttk.Label(summary, text="• " + line, wraplength=900, justify="left").pack(anchor="w", pady=2)

    # ------------------------------------------------------------ key management
    def _build_keys(self):
        f = self._tab("Key Management", "RSA Key Management",
                      "Generate an RSA key pair, display and export the public key, and store the private key "
                      "in a password-protected PEM file. Minimum size is 2048 bits.")
        row = ttk.Frame(f)
        row.pack(fill="x")
        ttk.Label(row, text="Key size (bits):").pack(side="left")
        self.size_var = tk.StringVar(value="2048")
        ttk.Combobox(row, textvariable=self.size_var, values=["2048", "3072", "4096"], width=8,
                     state="readonly").pack(side="left", padx=8)
        ttk.Button(row, text="Generate Key Pair", style="Accent.TButton",
                   command=self.generate_keys).pack(side="left")

        self.key_info = ttk.Label(f, text="", justify="left", wraplength=940)
        self.key_info.pack(anchor="w", pady=8)

        ttk.Label(f, text="Your public key (PEM) - safe to share:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        box, self.pub_text = self._text(f, height=9, readonly=True)
        box.pack(fill="both", expand=True)
        self._button_row(f, [
            ("Copy Public Key", self.copy_public_key, "TButton"),
            ("Export Public Key...", self.export_public_key, "TButton"),
            ("Import Public Key...", self.import_public_key, "TButton"),
            ("Use My Own Public Key", self.clear_recipient, "TButton"),
        ])
        self._button_row(f, [
            ("Export Private Key (encrypted)...", self.export_private_key, "TButton"),
            ("Import Private Key...", self.import_private_key, "TButton"),
        ])
        ttk.Label(f, text="The private key file is encrypted with your password. A forgotten password "
                          "cannot be recovered. Never share the private key.",
                  style="Muted.TLabel", wraplength=940).pack(anchor="w")
        self.key_result = self._result_label(f)

    def generate_keys(self):
        try:
            self.config(cursor="watch")
            self.set_status("Generating RSA key pair...")
            self.update_idletasks()
            self.private_key = rsa_keys.generate_key_pair(int(self.size_var.get()))
        except (ValidationError, ValueError) as exc:
            self.report(self.key_result, str(exc), False)
            return
        finally:
            self.config(cursor="")
        self.refresh_key_state()
        self.report(self.key_result, f"Generated a new {self.private_key.key_size}-bit RSA key pair.")

    def copy_public_key(self):
        if not self._need_private():
            return
        self.clipboard_clear()
        self.clipboard_append(self.get_text(self.pub_text))
        self.report(self.key_result, "Public key copied to clipboard.")

    def export_public_key(self):
        if not self._need_private():
            return
        path = filedialog.asksaveasfilename(title="Save public key", defaultextension=".pem",
                                            initialfile="public_key.pem",
                                            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")])
        if not path:
            return
        try:
            file_handler.write_text_file(path, self.get_text(self.pub_text))
        except OSError as exc:
            self.report(self.key_result, f"Could not save file: {exc.strerror or exc}", False)
            return
        self.report(self.key_result, f"Public key saved to {path}")

    def import_public_key(self):
        path = filedialog.askopenfilename(title="Import public key",
                                          filetypes=[("PEM files", "*.pem"), ("All files", "*.*")])
        if not path:
            return
        try:
            key = rsa_keys.load_public_key_pem(file_handler.read_bytes_file(path))
        except OSError as exc:
            self.report(self.key_result, f"Could not read file: {exc.strerror or exc}", False)
            return
        except rsa_keys.KeyError_ as exc:
            self.report(self.key_result, f"Import failed: {exc}", False)
            return
        if key.key_size < 2048:
            self.report(self.key_result, "Import rejected: key is smaller than 2048 bits.", False)
            return
        self.recipient_pub = key
        self.refresh_key_state()
        self.report(self.key_result, "Public key imported. It is now the recipient / verifier key.")

    def clear_recipient(self):
        self.recipient_pub = None
        self.refresh_key_state()
        self.report(self.key_result, "Using your own public key as recipient / verifier key.")

    def export_private_key(self):
        if not self._need_private():
            return
        try:
            pw = simpledialog.askstring("Protect private key", "Choose a password (min 8 characters):",
                                        show="*", parent=self)
            if pw is None:
                return
            pw2 = simpledialog.askstring("Protect private key", "Confirm the password:", show="*", parent=self)
            if pw2 is None:
                return
            require_password(pw, pw2)
            pem = rsa_keys.export_private_key_pem(self.private_key, pw)
        except ValidationError as exc:
            self.report(self.key_result, str(exc), False)
            return
        finally:
            pw = pw2 = None
        path = filedialog.asksaveasfilename(title="Save encrypted private key", defaultextension=".pem",
                                            initialfile="private_key_encrypted.pem",
                                            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")])
        if not path:
            return
        try:
            file_handler.write_private_file(path, pem)
        except OSError as exc:
            self.report(self.key_result, f"Could not save file: {exc.strerror or exc}", False)
            return
        self.report(self.key_result, f"Encrypted private key saved to {path}")

    def import_private_key(self):
        path = filedialog.askopenfilename(title="Import encrypted private key",
                                          filetypes=[("PEM files", "*.pem"), ("All files", "*.*")])
        if not path:
            return
        pw = simpledialog.askstring("Unlock private key", "Enter the key password:", show="*", parent=self)
        if pw is None:
            return
        try:
            key = rsa_keys.load_private_key_pem(file_handler.read_bytes_file(path), pw)
        except OSError as exc:
            self.report(self.key_result, f"Could not read file: {exc.strerror or exc}", False)
            return
        except rsa_keys.KeyError_ as exc:
            self.report(self.key_result, f"Import failed: {exc}", False)
            return
        finally:
            pw = None
        self.private_key = key
        self.refresh_key_state()
        self.report(self.key_result, "Private key imported successfully.")

    # -------------------------------------------------------------- encryption
    def _build_encrypt(self):
        f = self._tab("Encryption", "Encrypt with RSA-OAEP (SHA-256)",
                      "Encrypts a short message with the recipient's PUBLIC key. Direct RSA can only encrypt "
                      "a few bytes (190 bytes for 2048-bit keys); use the Hybrid tab for longer text.")
        self.enc_key_label = ttk.Label(f, text="", style="Muted.TLabel", justify="left")
        self.enc_key_label.pack(anchor="w")
        ttk.Label(f, text="Plaintext message:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 0))
        box, self.enc_in = self._text(f, height=5)
        box.pack(fill="x")
        self.enc_count = ttk.Label(f, text="", style="Muted.TLabel")
        self.enc_count.pack(anchor="w")
        self.enc_in.bind("<KeyRelease>", lambda _e: self._update_byte_count())
        self._button_row(f, [
            ("Encrypt", self.do_encrypt, "Accent.TButton"),
            ("Clear", lambda: (self.set_text(self.enc_in, ""), self.set_text(self.enc_out, ""),
                               self._update_byte_count()), "TButton"),
        ])
        ttk.Label(f, text="Ciphertext (Base64):", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        box, self.enc_out = self._text(f, height=8, readonly=True)
        box.pack(fill="both", expand=True)
        self._button_row(f, [
            ("Copy Ciphertext", lambda: self._copy(self.enc_out, self.enc_result), "TButton"),
            ("Save Ciphertext...", lambda: self._save(self.enc_out, self.enc_result, "ciphertext.txt"), "TButton"),
            ("Send to Decryption tab", self.send_to_decrypt, "TButton"),
        ])
        self.enc_result = self._result_label(f)

    def _update_byte_count(self):
        data = self.get_text(self.enc_in).encode("utf-8")
        pub = self.effective_public
        if pub:
            limit = enc.max_message_bytes(pub)
            self.enc_count.configure(text=f"{len(data)} / {limit} bytes",
                                     foreground=BAD if len(data) > limit else MUTED)
        else:
            self.enc_count.configure(text=f"{len(data)} bytes", foreground=MUTED)

    def do_encrypt(self):
        if not self._need_public():
            return
        try:
            ct = enc.encrypt_message(self.get_text(self.enc_in), self.effective_public)
        except ValidationError as exc:
            self.report(self.enc_result, str(exc), False)
            return
        self.set_text(self.enc_out, ct)
        self.report(self.enc_result, "Message encrypted. Ciphertext differs every time because OAEP is randomised.")

    def send_to_decrypt(self):
        value = self.get_text(self.enc_out)
        if not value:
            self.report(self.enc_result, "Nothing to send - encrypt a message first.", False)
            return
        self.set_text(self.dec_in, value)
        self.notebook.select(3)

    def _copy(self, widget, label):
        value = self.get_text(widget)
        if not value:
            self.report(label, "Nothing to copy.", False)
            return
        self.clipboard_clear()
        self.clipboard_append(value)
        self.report(label, "Copied to clipboard.")

    def _save(self, widget, label, default_name):
        value = self.get_text(widget)
        if not value:
            self.report(label, "Nothing to save.", False)
            return
        path = filedialog.asksaveasfilename(title="Save text", defaultextension=".txt", initialfile=default_name,
                                            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        try:
            file_handler.write_text_file(path, value)
        except OSError as exc:
            self.report(label, f"Could not save file: {exc.strerror or exc}", False)
            return
        self.report(label, f"Saved to {path}")

    def _load_into(self, widget, label):
        path = filedialog.askopenfilename(title="Open text file",
                                          filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        try:
            self.set_text(widget, file_handler.read_text_file(path).strip())
        except (OSError, UnicodeDecodeError) as exc:
            self.report(label, f"Could not read file: {exc}", False)
            return
        self.report(label, f"Loaded {path}")

    # -------------------------------------------------------------- decryption
    def _build_decrypt(self):
        f = self._tab("Decryption", "Decrypt with your RSA private key",
                      "Paste Base64 ciphertext made with your public key. Use the demo buttons to see what "
                      "happens with a wrong key or a modified ciphertext.")
        ttk.Label(f, text="Ciphertext (Base64):", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        box, self.dec_in = self._text(f, height=7)
        box.pack(fill="x")
        self._button_row(f, [
            ("Decrypt", self.do_decrypt, "Accent.TButton"),
            ("Load from File...", lambda: self._load_into(self.dec_in, self.dec_result), "TButton"),
            ("Demo: Try Wrong Key", self.demo_wrong_key, "TButton"),
            ("Demo: Tamper Ciphertext", self.demo_tamper, "TButton"),
        ])
        ttk.Label(f, text="Recovered plaintext:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        box, self.dec_out = self._text(f, height=7, readonly=True)
        box.pack(fill="both", expand=True)
        self.dec_result = self._result_label(f)

    def do_decrypt(self):
        if not self._need_private():
            return
        try:
            plain = enc.decrypt_message(self.get_text(self.dec_in), self.private_key)
        except (ValidationError, enc.DecryptionError) as exc:
            self.set_text(self.dec_out, "")
            self.report(self.dec_result, str(exc), False)
            return
        self.set_text(self.dec_out, plain)
        self.report(self.dec_result, "Decryption successful with the correct private key.")

    def demo_wrong_key(self):
        cipher = self.get_text(self.dec_in)
        if not cipher.strip():
            self.report(self.dec_result, "Paste or send a ciphertext first.", False)
            return
        self.set_status("Generating a different key pair for the demo...")
        self.update_idletasks()
        wrong = rsa_keys.generate_key_pair(2048)
        try:
            enc.decrypt_message(cipher, wrong)
        except (ValidationError, enc.DecryptionError) as exc:
            self.set_text(self.dec_out, "")
            self.report(self.dec_result, f"As expected, a wrong private key fails. Reason: {exc}", True)
            return
        self.report(self.dec_result, "Unexpected: the demo key decrypted the message.", False)

    def demo_tamper(self):
        cipher = self.get_text(self.dec_in)
        if not cipher.strip():
            self.report(self.dec_result, "Paste or send a ciphertext first.", False)
            return
        if not self._need_private():
            return
        try:
            bad = enc.tamper_ciphertext(cipher)
            enc.decrypt_message(bad, self.private_key)
        except (ValidationError, enc.DecryptionError) as exc:
            self.set_text(self.dec_out, "")
            self.report(self.dec_result, f"One bit was flipped and decryption failed, as expected. Reason: {exc}", True)
            return
        self.report(self.dec_result, "Unexpected: tampered ciphertext decrypted.", False)

    # -------------------------------------------------------------- signatures
    def _build_signature(self):
        f = self._tab("Digital Signature", "Sign and verify with RSA-PSS (SHA-256)",
                      "Sign with your PRIVATE key; anyone verifies with your PUBLIC key. A signature proves "
                      "who wrote the message and that it was not changed. It does NOT hide the message.")
        self.sig_key_label = ttk.Label(f, text="", style="Muted.TLabel", justify="left")
        self.sig_key_label.pack(anchor="w")
        ttk.Label(f, text="Message:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 0))
        box, self.sig_msg = self._text(f, height=5)
        box.pack(fill="x")
        self._button_row(f, [
            ("Sign Message", self.do_sign, "Accent.TButton"),
            ("Verify Signature", self.do_verify, "Accent.TButton"),
            ("Demo: Tamper Message & Verify", self.demo_sig_tamper, "TButton"),
            ("Demo: Verify With Wrong Key", self.demo_sig_wrong_key, "TButton"),
        ])
        ttk.Label(f, text="Signature (Base64):", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        box, self.sig_val = self._text(f, height=7)
        box.pack(fill="both", expand=True)
        self._button_row(f, [
            ("Copy Signature", lambda: self._copy(self.sig_val, self.sig_result), "TButton"),
            ("Save Signature...", lambda: self._save(self.sig_val, self.sig_result, "signature.txt"), "TButton"),
            ("Load Signature...", lambda: self._load_into(self.sig_val, self.sig_result), "TButton"),
        ])
        self.sig_result = self._result_label(f)

    def do_sign(self):
        if not self._need_private():
            return
        try:
            value = sigs.sign_message(self.get_text(self.sig_msg), self.private_key)
        except ValidationError as exc:
            self.report(self.sig_result, str(exc), False)
            return
        self.set_text(self.sig_val, value)
        self.report(self.sig_result, "Message signed with your private key (RSA-PSS, SHA-256).")

    def _verify_with(self, message, key, wrong=False):
        try:
            return sigs.verify_signature(message, self.get_text(self.sig_val), key)
        except ValidationError as exc:
            self.report(self.sig_result, str(exc), False)
            return None

    def do_verify(self):
        if not self._need_public():
            return
        ok = self._verify_with(self.get_text(self.sig_msg), self.effective_public)
        if ok is None:
            return
        if ok:
            self.report(self.sig_result, "VALID: the signature matches the message and the public key.")
        else:
            self.report(self.sig_result, "INVALID: wrong key, modified message, or corrupted signature.", False)

    def demo_sig_tamper(self):
        if not self._need_public():
            return
        message = self.get_text(self.sig_msg)
        if not message.strip():
            self.report(self.sig_result, "Message must not be empty.", False)
            return
        tampered = message + " (edited)"
        ok = self._verify_with(tampered, self.effective_public)
        if ok is None:
            return
        self.set_text(self.sig_msg, tampered)
        if ok:
            self.report(self.sig_result, "Unexpected: tampered message verified.", False)
        else:
            self.report(self.sig_result, "Message was modified after signing, so verification FAILED as expected. "
                                         "The message box now shows the edited text.", True)

    def demo_sig_wrong_key(self):
        message = self.get_text(self.sig_msg)
        self.set_status("Generating a different key pair for the demo...")
        self.update_idletasks()
        wrong = rsa_keys.generate_key_pair(2048).public_key()
        ok = self._verify_with(message, wrong)
        if ok is None:
            return
        if ok:
            self.report(self.sig_result, "Unexpected: wrong key verified the signature.", False)
        else:
            self.report(self.sig_result, "Verification with a different public key FAILED as expected.", True)

    # ------------------------------------------------------------------ hybrid
    def _build_hybrid(self):
        f = self._tab("Hybrid Encryption", "Hybrid encryption: AES-256-GCM + RSA-OAEP",
                      "For messages of any length. A fresh random AES key encrypts the text; that key is wrapped "
                      "with RSA-OAEP. The result is a Base64 JSON envelope (version, alg, wrapped_key, nonce, "
                      "ciphertext). AES-GCM detects any modification.")
        self.hyb_key_label = ttk.Label(f, text="", style="Muted.TLabel", justify="left")
        self.hyb_key_label.pack(anchor="w")
        ttk.Label(f, text="Message / envelope input:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 0))
        box, self.hyb_in = self._text(f, height=8)
        box.pack(fill="both", expand=True)
        self._button_row(f, [
            ("Encrypt (input → envelope)", self.do_hybrid_encrypt, "Accent.TButton"),
            ("Decrypt (envelope → text)", self.do_hybrid_decrypt, "Accent.TButton"),
            ("Demo: Tamper Envelope & Decrypt", self.demo_hybrid_tamper, "TButton"),
            ("Insert Sample Long Text", self.insert_sample, "TButton"),
        ])
        ttk.Label(f, text="Output:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        box, self.hyb_out = self._text(f, height=8, readonly=True)
        box.pack(fill="both", expand=True)
        self._button_row(f, [
            ("Copy Output", lambda: self._copy(self.hyb_out, self.hyb_result), "TButton"),
            ("Save Output...", lambda: self._save(self.hyb_out, self.hyb_result, "envelope.txt"), "TButton"),
            ("Move Output to Input", self.hyb_swap, "TButton"),
        ])
        self.hyb_result = self._result_label(f)

    def insert_sample(self):
        sample = ("SecureText hybrid demo. RSA alone can only encrypt about 190 bytes with a 2048-bit key, "
                  "so for longer messages a random AES-256 key encrypts the text with AES-GCM and RSA-OAEP "
                  "protects only that small key. ") * 4
        self.set_text(self.hyb_in, sample)
        self.report(self.hyb_result, f"Inserted sample text ({len(sample.encode('utf-8'))} bytes).")

    def do_hybrid_encrypt(self):
        if not self._need_public():
            return
        try:
            env = hybrid.encrypt_hybrid(self.get_text(self.hyb_in), self.effective_public)
        except ValidationError as exc:
            self.report(self.hyb_result, str(exc), False)
            return
        self.set_text(self.hyb_out, env)
        self.report(self.hyb_result, "Encrypted with a fresh AES-256 key and nonce; AES key wrapped with RSA-OAEP.")

    def do_hybrid_decrypt(self):
        if not self._need_private():
            return
        try:
            plain = hybrid.decrypt_hybrid(self.get_text(self.hyb_in), self.private_key)
        except (ValidationError, enc.DecryptionError) as exc:
            self.set_text(self.hyb_out, "")
            self.report(self.hyb_result, str(exc), False)
            return
        self.set_text(self.hyb_out, plain)
        self.report(self.hyb_result, "Decrypted and authenticated successfully.")

    def demo_hybrid_tamper(self):
        if not self._need_private():
            return
        try:
            bad = hybrid.tamper_envelope(self.get_text(self.hyb_in))
            hybrid.decrypt_hybrid(bad, self.private_key)
        except (ValidationError, enc.DecryptionError) as exc:
            self.set_text(self.hyb_out, "")
            self.report(self.hyb_result, f"One bit was flipped and decryption failed, as expected. Reason: {exc}", True)
            return
        self.report(self.hyb_result, "Unexpected: tampered envelope decrypted.", False)

    def hyb_swap(self):
        value = self.get_text(self.hyb_out)
        if not value:
            self.report(self.hyb_result, "Nothing to move.", False)
            return
        self.set_text(self.hyb_in, value)
        self.set_text(self.hyb_out, "")

    # --------------------------------------------------------------------- math
    def _build_math(self):
        f = self._tab("RSA Math", "RSA mathematics (educational)",
                      "Left: theory. Right: a toy calculator with tiny primes. The toy example is NOT secure and "
                      "is only for understanding the arithmetic.")
        pane = ttk.Frame(f)
        pane.pack(fill="both", expand=True)
        left = ttk.Frame(pane)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        box, theory = self._text(left, height=20, readonly=True)
        box.pack(fill="both", expand=True)
        self.set_text(theory, MATH_TEXT)

        right = ttk.LabelFrame(pane, text="Toy RSA calculator (tiny primes)", padding=10)
        right.pack(side="right", fill="both", expand=True)
        self.toy_vars = {}
        for name, default in (("p", "61"), ("q", "53"), ("e", "17"), ("m", "65")):
            row = ttk.Frame(right)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=f"{name} =", width=4).pack(side="left")
            var = tk.StringVar(value=default)
            ttk.Entry(row, textvariable=var, width=14).pack(side="left")
            self.toy_vars[name] = var
        ttk.Button(right, text="Run toy RSA", style="Accent.TButton", command=self.run_toy).pack(anchor="w", pady=6)
        box, self.toy_out = self._text(right, height=14, readonly=True)
        box.pack(fill="both", expand=True)
        ttk.Button(right, text="Show my real key sizes", command=self.show_real_key).pack(anchor="w", pady=6)
        self.math_result = self._result_label(right)

    def run_toy(self):
        try:
            values = {k: int(v.get().strip()) for k, v in self.toy_vars.items()}
        except ValueError:
            self.report(self.math_result, "p, q, e and m must be whole numbers.", False)
            return
        try:
            steps = toy_rsa_walkthrough(values["p"], values["q"], values["e"], values["m"])
        except ToyRSAError as exc:
            self.set_text(self.toy_out, "")
            self.report(self.math_result, str(exc), False)
            return
        self.set_text(self.toy_out, "\n".join(steps))
        self.report(self.math_result, "Toy RSA computed (insecure demo numbers).")

    def show_real_key(self):
        if not self._need_private():
            return
        n, e = rsa_keys.public_numbers(self.private_key)
        p, q, d = rsa_keys.private_numbers(self.private_key)
        lines = [
            "REAL KEY (values of p, q and d are secret and are NOT displayed)",
            f"Modulus n: {n.bit_length()} bits (public)",
            f"Public exponent e: {e}",
            f"p: {p.bit_length()} bits    q: {q.bit_length()} bits    d: {d.bit_length()} bits",
            "The real application uses OAEP/PSS padding, never textbook RSA.",
        ]
        self.set_text(self.toy_out, "\n".join(lines))
        self.report(self.math_result, "Showing sizes only; secret values are never displayed.")

    # --------------------------------------------------------------------- help
    def _build_help(self):
        f = self._tab("About & Help", "About and Help", "How to use SecureText and what it demonstrates.")
        box, widget = self._text(f, height=24, readonly=True)
        box.pack(fill="both", expand=True)
        self.set_text(widget, ABOUT_TEXT + "\n" + HELP_TEXT)


def run():
    app = SecureTextApp()
    app.mainloop()


if __name__ == "__main__":
    run()
