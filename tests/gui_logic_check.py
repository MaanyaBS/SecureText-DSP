"""Headless smoke check of gui/main_window.py using a FAKE tkinter.

Run from the project root:  python tests/gui_logic_check.py


NOT a real GUI test: it only checks that handlers are wired to the crypto layer
and that no attribute/name errors occur. Real rendering is not exercised.
"""
import os
import sys
import tempfile
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class Fake:
    def __init__(self, *a, **k):
        self.opts = dict(k)
        self.content = ""

    def configure(self, *a, **k):
        self.opts.update(k)

    config = configure

    def cget(self, k):
        return self.opts.get(k)

    def get(self, *a):
        return self.content

    def insert(self, idx, value):
        self.content = value

    def delete(self, *a):
        self.content = ""

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return lambda *a, **k: None


class FakeVar:
    def __init__(self, value=""):
        self.v = value

    def get(self):
        return self.v

    def set(self, v):
        self.v = v


tk = types.ModuleType("tkinter")
tk.Tk = Fake
tk.Frame = Fake
tk.Label = Fake
tk.Text = Fake
tk.StringVar = FakeVar
tk.TclError = Exception
ttk = types.ModuleType("tkinter.ttk")
for name in ("Frame", "Label", "Button", "Combobox", "Entry", "Notebook", "Scrollbar", "LabelFrame", "Style"):
    setattr(ttk, name, Fake)
mb = types.ModuleType("tkinter.messagebox")
mb.warned = []
mb.showwarning = lambda *a, **k: mb.warned.append(a)
fd = types.ModuleType("tkinter.filedialog")
sd = types.ModuleType("tkinter.simpledialog")
tk.ttk, tk.messagebox, tk.filedialog, tk.simpledialog = ttk, mb, fd, sd
sys.modules.update({"tkinter": tk, "tkinter.ttk": ttk, "tkinter.messagebox": mb,
                    "tkinter.filedialog": fd, "tkinter.simpledialog": sd})

from gui.main_window import SecureTextApp, OK, BAD  # noqa: E402

app = SecureTextApp()
checks = []


def check(name, cond):
    checks.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name)


def last(label):
    return label.opts.get("text", ""), label.opts.get("foreground")


# no key yet -> warnings, no crash
app.do_encrypt()
check("encrypt without key warns", len(mb.warned) == 1)

app.size_var.set("2048")
app.generate_keys()
check("generate_keys sets key", app.private_key is not None and app.private_key.key_size == 2048)
check("public key shown", "BEGIN PUBLIC KEY" in app.pub_text.content)

# encryption / decryption
app.set_text(app.enc_in, "Hello SecureText")
app.do_encrypt()
check("encrypt output present", len(app.enc_out.content) > 100)
app.send_to_decrypt()
app.do_decrypt()
check("decrypt roundtrip", app.dec_out.content == "Hello SecureText")
app.demo_wrong_key()
check("wrong key demo reports expected failure", last(app.dec_result)[1] == OK and "wrong" in last(app.dec_result)[0].lower())
app.demo_tamper()
check("tamper demo reports expected failure", last(app.dec_result)[1] == OK and "flipped" in last(app.dec_result)[0])
app.set_text(app.enc_in, "x" * 300)
app.do_encrypt()
check("oversize message error shown", last(app.enc_result)[1] == BAD and "Hybrid" in last(app.enc_result)[0])
app.set_text(app.dec_in, "not base64!!")
app.do_decrypt()
check("invalid ciphertext error shown", last(app.dec_result)[1] == BAD)
app.set_text(app.enc_in, "")
app.do_encrypt()
check("empty message rejected", last(app.enc_result)[1] == BAD)

# signatures
app.set_text(app.sig_msg, "Pay Alice 100")
app.do_sign()
check("signature produced", len(app.sig_val.content) > 100)
app.do_verify()
check("valid signature verifies", last(app.sig_result)[1] == OK and last(app.sig_result)[0].startswith("VALID"))
app.demo_sig_tamper()
check("tamper demo fails verification as expected", "FAILED as expected" in last(app.sig_result)[0])
app.set_text(app.sig_msg, "Pay Alice 100")
app.do_verify()
check("restored message verifies again", last(app.sig_result)[0].startswith("VALID"))
app.demo_sig_wrong_key()
check("wrong public key demo", "FAILED as expected" in last(app.sig_result)[0])
app.set_text(app.sig_val, "")
app.do_verify()
check("empty signature rejected", last(app.sig_result)[1] == BAD)

# hybrid
app.insert_sample()
app.do_hybrid_encrypt()
env = app.hyb_out.content
check("hybrid envelope produced", len(env) > 200)
app.hyb_swap()
app.do_hybrid_decrypt()
check("hybrid decrypt returns sample", app.hyb_out.content.startswith("SecureText hybrid demo"))
app.set_text(app.hyb_in, env)
app.demo_hybrid_tamper()
check("hybrid tamper demo", last(app.hyb_result)[1] == OK and "flipped" in last(app.hyb_result)[0])

# math tab
app.run_toy()
check("toy rsa output", "= 2790" in app.toy_out.content)
app.toy_vars["p"].set("60")
app.run_toy()
check("toy rsa invalid p", last(app.math_result)[1] == BAD)
app.show_real_key()
check("real key sizes only (no secret values)", "2048 bits" in app.toy_out.content and
      str(app.private_key.private_numbers().d) not in app.toy_out.content)

# key files
tmp = tempfile.mkdtemp()
priv, pub = os.path.join(tmp, "priv.pem"), os.path.join(tmp, "pub.pem")
answers = iter(["strong pass 1", "strong pass 1"])
sd.askstring = lambda *a, **k: next(answers)
fd.asksaveasfilename = lambda **k: priv
app.export_private_key()
check("private key file written and encrypted", os.path.exists(priv) and b"ENCRYPTED PRIVATE KEY" in open(priv, "rb").read())
fd.asksaveasfilename = lambda **k: pub
app.export_public_key()
check("public key file written", os.path.exists(pub))

old_numbers = app.private_key.private_numbers()
app.private_key = None
fd.askopenfilename = lambda **k: priv
sd.askstring = lambda *a, **k: "wrong password"
app.import_private_key()
check("wrong password import rejected", app.private_key is None and last(app.key_result)[1] == BAD)
sd.askstring = lambda *a, **k: "strong pass 1"
app.import_private_key()
check("correct password import works", app.private_key is not None and app.private_key.private_numbers() == old_numbers)
fd.askopenfilename = lambda **k: pub
app.import_public_key()
check("public key import sets recipient", app.recipient_pub is not None)
app.clear_recipient()
check("recipient cleared", app.recipient_pub is None)
bad = os.path.join(tmp, "bad.pem")
open(bad, "w").write("garbage")
fd.askopenfilename = lambda **k: bad
app.import_public_key()
check("garbage public key rejected", last(app.key_result)[1] == BAD)

# mismatched mismatch: password too short on export
answers = iter(["short", "short"])
sd.askstring = lambda *a, **k: next(answers)
app.export_private_key()
check("short password rejected", "at least 8" in last(app.key_result)[0])

failed = [n for n, ok in checks if not ok]
print(f"\n{len(checks) - len(failed)}/{len(checks)} stub smoke checks passed")
sys.exit(1 if failed else 0)
