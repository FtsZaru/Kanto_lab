import pandas as pd
import streamlit as st
import json



#Open save file, JSON dictionaries


uploaded_file = st.file_uploader("Upload a Save File", type=["sav"])
if uploaded_file is None:
      
    with open('Kantolab.sav', 'rb') as sf:
        savedata = bytearray(sf.read())
    st.write("Upload a Save File")


if uploaded_file is not None:
    savedata = bytearray(uploaded_file.getvalue())
    st.write("File uploaded")
    

with open ('species.json', 'r', encoding = 'utf-8') as f:
      species_to_id=json.load(f)

with open ('moves.json', 'r', encoding = 'utf-8') as f:
      move_to_index=json.load(f)

with open ('status.json', 'r', encoding = 'utf-8') as f:
      status=json.load(f)

with open ('type.json', 'r', encoding = 'utf-8') as f:
      type_to_index=json.load(f)
with open ('char_byte.json', 'r', encoding = 'utf-8') as f:
      gen1_byte_to_char=json.load(f)
gen1_byte_to_char_corr = {int(byte):char for byte,char in gen1_byte_to_char.items()}




#reverse dictionaries
  
species_to_id_reverse = {Index:Name for Name, Index in species_to_id.items()}
Index_to_moves = {Index:Move for Move, Index in move_to_index.items()}   
index_to_status = {i:s for s,i in status.items()}
index_to_type = {index:type for type, index in type_to_index.items()}
gen1_char_to_byte = {char:byte for byte, char in gen1_byte_to_char_corr.items()}

#read 16- and 24-bit values
def read_16bit (savedata, PARTY_COUNTER):
        return int.from_bytes(savedata[PARTY_COUNTER:PARTY_COUNTER+2], 
                              'big')
def read_24bit (savedata, PARTY_COUNTER):
        return int.from_bytes(savedata[PARTY_COUNTER:PARTY_COUNTER+3],
                              'big')

PARTY_OFFSET = 0x2F2C
PARTY_BLOCK = 0x2F34
TRAINER_OFFSET = 0x303C
TRAINER_NAME= ""
Party_Data = []
count = savedata[PARTY_OFFSET]

#break stops loop, place after for logic
for name in savedata[TRAINER_OFFSET:TRAINER_OFFSET + 11]:
    if name == 80: break 
    TRAINER_NAME += gen1_byte_to_char_corr[name]
     
Party_Data = []    
for i in range(count):

    PARTY_COUNTER = PARTY_BLOCK + 44 * i
    Species = savedata[PARTY_COUNTER]
    CURRENT_HP = read_16bit(savedata,PARTY_COUNTER + 1)
    STATUS = savedata[PARTY_COUNTER +4]

    Type_01 = savedata[PARTY_COUNTER + 5]
    Type_02 = savedata[PARTY_COUNTER + 6]
    if Type_01 == Type_02:
          Type_02=27


    CATCH_RATE=savedata[PARTY_COUNTER + 7]
    MOVE_01 = Index_to_moves[savedata[PARTY_COUNTER + 8]]
    MOVE_02 = Index_to_moves[savedata[PARTY_COUNTER + 9]]
    MOVE_03 = Index_to_moves[savedata[PARTY_COUNTER + 10]]
    MOVE_04 = Index_to_moves[savedata[PARTY_COUNTER + 11]]
    OT =   read_16bit(savedata,PARTY_COUNTER + 12)
    EXP =  read_24bit(savedata,PARTY_COUNTER + 14)
    HPEV = read_16bit(savedata,PARTY_COUNTER + 17)
    ATKEV =read_16bit(savedata,PARTY_COUNTER + 19)
    DEFEV =read_16bit(savedata,PARTY_COUNTER + 21)
    SPDEV =read_16bit(savedata,PARTY_COUNTER + 23)
    SPEDEV=read_16bit(savedata,PARTY_COUNTER + 25)
    ATK_DV = savedata[PARTY_COUNTER + 27] >> 4
    DEF_DV = savedata[PARTY_COUNTER + 27] & 0x0F
    SPEED_DV = savedata[PARTY_COUNTER + 28] >> 4
    SPECIAL_DV = savedata[PARTY_COUNTER + 28] & 0x0F
    HP_DV = (ATK_DV & 1)<<3| (DEF_DV & 1)<<2| (SPEED_DV & 1)<<1| (SPECIAL_DV & 1)
    PP1=savedata[PARTY_COUNTER+29]
    PP2=savedata[PARTY_COUNTER+30]
    PP3=savedata[PARTY_COUNTER+31]
    PP4=savedata[PARTY_COUNTER+32]
    LEVEL = savedata[PARTY_COUNTER + 33]
    MaxHP =read_16bit(savedata, PARTY_COUNTER +34) 
    ATK =read_16bit(savedata, PARTY_COUNTER +36) 
    DEF = read_16bit(savedata, PARTY_COUNTER +38) 
    SPD = read_16bit(savedata, PARTY_COUNTER +40) 
    SPE = read_16bit(savedata, PARTY_COUNTER +42) 


    #each loop appends a new list containing a dictionary. The final result is a list of dictionaries for
    #the entire party.
  
    Party_Data.append({"SLOT":i + 1,
    "SPECIES":species_to_id_reverse[Species],
    "LEVEL":LEVEL,
    "CURRENT HP":CURRENT_HP,
    "MAX HP":MaxHP,
    "STATUS":index_to_status[STATUS],
    "TYPE 01":index_to_type[Type_01],"TYPE 02": index_to_type[Type_02],    
    "IDNo":OT,  
    "OT":TRAINER_NAME,
    "ATTACK":ATK,"DEFENSE":DEF,"SPEED":SPD,"SPECIAL":SPE,
    "EXPERIENCE":EXP,
    "MOVE 01":MOVE_01,"MOVE 02":MOVE_02,"MOVE 03":MOVE_03,"MOVE 04":MOVE_04,
    "HP EV":HPEV,"ATTACK EV": ATKEV,"DEFENSE EV":DEFEV,"SPEED EV":SPDEV,"SPECIAL EV":SPEDEV,
    "HP DV":HP_DV,"ATTACK DV":ATK_DV,"DEFENSE DV":DEF_DV,"SPEED DV":SPEED_DV,"SPECIAL DV":SPECIAL_DV,
    }) 
    
    #creates a dataframe from the list of dictionaries. sets rows as SLOT, then reverse rows and columns (stats as rows, slot as columns)
PARTYdf= pd.DataFrame(Party_Data).set_index("SLOT").T

print(PARTYdf)
if uploaded_file is None:
    
      st.dataframe(pd.DataFrame())  
if uploaded_file is not None:
    st.dataframe(PARTYdf, use_container_width=True)   

#print(PARTYdf[4])
#PARTYdf.to_excel("Party_df.xlsx")



    
    
    
    
    
    #print("Species:",species_to_id_reverse[Species])
    #print("LEVEL:", LEVEL)
    #if Type_01 == Type_02:
        #print("Type:",index_to_type[Type_01])
    #else: print("Type:", index_to_type[Type_01],index_to_type[Type_02])
    #print("STATUS:",index_to_status[STATUS])
    #print("HP:",CURRENT_HP)
    #print("EXPERIENCE:", EXP)
    #print("MOVE 01:", MOVE_01,"PP:",PP1)
    #print("MOVE 02:", MOVE_02,"PP",PP2)
    #print("MOVE 03:", MOVE_03,"PP",PP3)
    #print("MOVE 04:", MOVE_04,"PP",PP4)
    #print("OT:",OT)
    #print("Active Stats:","Max HP", MaxHP,"ATK", ATK,"DEF",DEF,"SPD",SPD,"SPE",SPE)
    #print("EVs:", "HP", HPEV, "ATK",ATKEV, "DEF", DEFEV, "SPD",SPDEV, "SPE", SPEDEV)
    #print("DVs:","HP:", HP_DV, "ATK",ATK_DV, "DEF", DEF_DV, "SPD",SPEED_DV, "SPE", SPECIAL_DV)
    
    
