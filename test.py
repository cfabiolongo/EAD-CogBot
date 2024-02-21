def wfc(cmd, str):
    # Controlla se la stringa inizia con "proc(" e termina con ")"
    if str.startswith(f"{cmd}(") and str.endswith(")"):
        # Controlla se all'interno delle parentesi ci sia almeno un carattere
        if len(str) > 6:
            return True
    return False

# Esempi di utilizzo
stringa1 = "proc(\"hello\")"
stringa2 = "proc()"
stringa3 = "proc(\"world\")"
stringa4 = "procbadformat"

print(wfc("proc", stringa1))  # Output: True
print(wfc("proc", stringa2))  # Output: False
print(wfc("proc", stringa3))  # Output: True
print(wfc("proc", stringa4))  # Output: False