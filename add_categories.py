import re

with open('src/components/InventoryTab.svelte', 'r') as f:
    content = f.read()

new_options = """                          <option value="Tablet">Tablet</option>
                          <option value="Syrup">Syrup</option>
                          <option value="Powder">Powder</option>
                          <option value="Ointment/Gel">Ointment/Gel</option>
                          <option value="Injection Vial">Injection Vial</option>
                          <option value="Injection Ampule">Injection Ampule</option>
                          <option value="Liquid">Liquid</option>
                          <option value="Bolus">Bolus</option>
                          <option value="Syringe">Syringe</option>
                          <option value="Needle">Needle</option>
                          <option value="IV Set">IV Set</option>
                          <option value="SV Set">SV Set</option>
                          <option value="Condom">Condom</option>
                          <option value="Spray">Spray</option>
                          <option value="Bandage">Bandage</option>
                          <option value="Band Aid">Band Aid</option>"""

# Replace in inv-category
pattern1 = re.compile(r'<option value="Tablet">Tablet</option>.*?<option value="Injection Ampule">Injection Ampule</option>', re.DOTALL)
content = pattern1.sub(new_options, content)

with open('src/components/InventoryTab.svelte', 'w') as f:
    f.write(content)

print("Added categories successfully.")
