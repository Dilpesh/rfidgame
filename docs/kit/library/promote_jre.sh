# Reusable Jungle Rescue English lines and sounds → the shared library.
L="python3 docs/kit/tools/library.py"; S=jungle-rescue-english
P() { $L promote "$@" >/dev/null || echo "FAILED: $*"; }
# Coco (Saanu), Hindi — openings and framing
P $S JR_002 --id hello_coco --desc "Coco's hello: हैलो, मैं हूँ कोको। आज हम जंगल बचाओ टीम बनेंगे।" --tags coco,hello,intro,jungle
P $S JR_003 --id captain_help --desc "Coco asks the child to be Captain and help: जंगल में हमारे कई दोस्त मुसीबत में हैं… क्या तुम Captain बनकर मेरी मदद करोगे?" --tags coco,intro,captain,invite
P $S JR_004 --id yes_great --desc "Coco, delighted: Yes! Great! अब Captain और कोको मिलकर सारे animals को बचा लेंगे।" --tags coco,yes,great,intro
P $S JR_005 --id jeep_ready --desc "Coco: जल्दी चलो, हमारी जंगल रेस्क्यू जीप तैयार है।" --tags coco,jeep,go
P $S JR_007 --id narr_jeep_start --desc "Narrator (Jia): कोको जीप में बैठा, स्टीयरिंग पकड़ी, चाबी घुमाई।" --tags narrator,jeep,start
P $S JR_009 --id tank_empty --desc "Coco, surprised: ओह, ये स्टार्ट क्यों नहीं हो रही है? हम्म, जीप की टंकी खाली है।" --tags coco,jeep,fuel,empty
P $S JR_010 --id ask_fuel --desc "FUEL question: Captain, टंकी खाली है! इसमें क्या डालें कि जीप चल पड़े?" --tags coco,ask,fuel,question
P $S JR_011 --id hint_fuel_1 --desc "FUEL hint 1: अपने सामने वाले cards को देखो... इनमें Jeep को चलाने वाली कोई चीज़ है क्या?" --tags coco,hint,fuel
P $S JR_012 --id hint_fuel_2 --desc "FUEL hint 2: जिससे गाड़ी की tank भरती है, वही card ढूँढो." --tags coco,hint,fuel
P $S JR_013 --id hint_fuel_3 --desc "FUEL rescue hint: FUEL वाला card scan करो." --tags coco,hint,fuel,rescue
P $S JR_015 --id yes_fuel --desc "FUEL praise: YES! FUEL! टंकी भर गई!" --tags coco,praise,yes,fuel
P $S JR_018 --id rescue_team_chalo --desc "Coco's rallying call: जंगल रेस्क्यू टीम चलो!" --tags coco,rally,go,chalo
P $S JR_022 --id narr_jungle_drive --desc "Narrator: जीप जंगल के अंदर गई। बड़े-बड़े पेड़, छोटी-छोटी नदियाँ, उछलती-कूदती जीप!" --tags narrator,jeep,drive,jungle
P $S JR_026 --id trampoline_joke --desc "Coco joke on a bumpy road: वो! ये रोड है या ट्रैम्पोलीन?" --tags coco,joke,jeep,bump
P $S JR_104 --id narr_night_arrival --desc "Narrator, hushed: रेस्क्यू जीप घने जंगलों के बीच आकर रुकी। सूरज ढल चुका था…" --tags narrator,night,dark,arrive
P $S JR_115 --id ask_torch --desc "FLASHLIGHT question: अरे! इतना अंधेरा है कि मेरी नाक भी नहीं दिख रही! Captain, हमें तुरंत रोशनी चाहिए…" --tags coco,ask,torch,flashlight,dark,question
P $S JR_116 --id hint_torch_1 --desc "FLASHLIGHT hint 1: अपने cards में देखो... कोई ऐसी चीज़ है जो अंधेरे में तेज़ रोशनी दे सके?" --tags coco,hint,torch,flashlight
P $S JR_117 --id hint_torch_2 --desc "FLASHLIGHT hint 2: इसे ON करते ही अंधेरे में रास्ता साफ़ दिखने लगता है।" --tags coco,hint,torch,flashlight
P $S JR_118 --id hint_torch_3 --desc "FLASHLIGHT rescue hint: FLASHLIGHT वाला card scan करो!" --tags coco,hint,torch,flashlight,rescue
P $S JR_121 --id yes_torch --desc "FLASHLIGHT praise: YES! FLASHLIGHT!" --tags coco,praise,yes,torch,flashlight
P $S JR_123 --id owl_joke --desc "Coco, light comes on: वाह! रोशनी होते ही सब दिखने लगा! ...और rock के ऊपर वो उल्लू भी!" --tags coco,joke,owl,light
P $S JR_094 --id ask_water --desc "WATER break instruction: पहले असली पानी पियो, फिर WATER वाला card tap करो (action first, card second)" --tags coco,ask,water,break,action,question
P $S JR_095 --id remind_water --desc "WATER break reminder: Captain, Coco यहीं wait कर रहा है। पानी पीकर आओ और WATER वाला card tap कर देना।" --tags coco,water,remind
P $S JR_097 --id welcome_back --desc "After the water break: Welcome back, Captain! अब पैरट को भी थोड़ा water देते हैं। (mentions the parrot)" --tags coco,water,welcome,parrot
P $S JR_152 --id party_time --desc "Coco, proud: Captain, हमने दोस्तों की मदद कर दी! अब हमारी पार्टी!" --tags coco,party,celebrate
P $S JR_154 --id ask_music --desc "MUSIC question: मेरे पैर तो नाचने लगे! पर धुन कहाँ है? Captain, नाचने के लिए क्या बजाएँ?" --tags coco,ask,music,dance,question
P $S JR_155 --id hint_music_1 --desc "MUSIC hint 1: पार्टी में नाचने के लिए धुन चाहिए।" --tags coco,hint,music
P $S JR_156 --id hint_music_2 --desc "MUSIC hint 2: गाना बजाने वाला card ढूँढो।" --tags coco,hint,music
P $S JR_157 --id hint_music_3 --desc "MUSIC rescue hint: MUSIC वाला card tap करो।" --tags coco,hint,music,rescue
P $S JR_159 --id yes_music --desc "MUSIC praise: YES! MUSIC!" --tags coco,praise,yes,music
P $S JR_161 --id dance_elephant --desc "Dance call, over the music: Elephant dance! हाथ की सूँड़ बनाओ — इधर, उधर! बैठे-बैठे भी!" --tags coco,dance,elephant,action
P $S JR_163 --id freeze_statue --desc "Freeze call (fits in 3 s): Freeze! मूर्ति बन जाओ!" --tags coco,dance,freeze,action
P $S JR_164 --id dance_parrot --desc "Dance call: Parrot dance! हाथों के पंख — फड़फड़, फड़फड़!" --tags coco,dance,parrot,action
P $S JR_166 --id freeze_cheeks --desc "Freeze call (fits in 3 s): Freeze! गाल फुलाओ!" --tags coco,dance,freeze,action,cheeks
P $S JR_167 --id dance_captain --desc "Dance call: पुफ्फ! अब Captain वाला dance! हाथ हिलाओ या ताली बजाओ!" --tags coco,dance,captain,action
P $S JR_171 --id thank_you_captain --desc "Ending: Captain, तुम्हारी मदद से हमारे दोस्त फिर खुश हैं। Thank you, Captain!" --tags coco,thanks,ending,praise
P $S JR_172 --id hands_up --desc "Ending chant: हाथ ऊपर! साथ बोलो — हम हैं जंगल बचाओ टीम!" --tags coco,ending,chant,action
P $S JR_173 --id high_five --desc "Coco: मेरी तरफ हवा में high-five!" --tags coco,ending,high-five,action
P $S JR_175 --id mud_hands_joke --desc "Coco joke after the high-five: अरे! मेरे हाथ पर अभी भी कीचड़ है!" --tags coco,joke,mud,ending
P $S JR_177 --id bye_captain --desc "Coco's goodbye: ये कौन करता है?! पहले हाथ धोऊँगा! Bye-bye, Captain!" --tags coco,bye,ending
P $S JR_180 --id wrong_1 --desc "Wrong card, warm: ओहो! ये वाला काम नहीं करेगा। Captain, एक और card try करो!" --tags coco,wrong,retry,warm
P $S JR_182 --id wrong_2 --desc "Wrong card, warm: ऊप्स! हमें कोई और चीज़ चाहिए। Captain, फिर से सोचो!" --tags coco,wrong,retry,warm
P $S JR_184 --id wrong_3 --desc "Wrong card, warm: हम्म... ये नहीं। Captain, दूसरा card try करो!" --tags coco,wrong,retry,warm
# sounds
P $S JR_006 --id jeep_door --desc "jeep door opens, quick" --tags jeep,door,sfx
P $S JR_008 --id key_engine_cough --desc "key turn then two comic engine coughs — the jeep will not start" --tags jeep,key,engine,cough,funny
P $S JR_016 --id fuel_pour --desc "short fuel pouring / tank filling" --tags fuel,pour,jeep
P $S JR_017 --id engine_start --desc "engine catches and starts" --tags engine,start,jeep
P $S JR_023 --id jeep_bump --desc "one soft jeep bump on a bad road" --tags jeep,bump,road
P $S JR_027 --id elephant_trumpet --desc "friendly elephant trumpet, full and clear" --tags elephant,trumpet,animal
P $S JR_103 --part jeep_file --id jeep_arrive_stop --desc "jeep drives up on gravel and stops, engine off (~4.5 s)" --tags jeep,arrive,stop,gravel
P $S JR_120 --id torch_click --desc "torch / flashlight click on" --tags torch,click,light
P $S JR_122 --id light_sweep --desc "light sweeping across a scene" --tags light,sweep,torch
P $S JR_124 --id owl_hoot --desc "an owl hoots, night" --tags owl,hoot,night,animal
P $S JR_170 --id music_end_flourish --desc "short musical flourish that ends the dance" --tags music,end,flourish
P $S JR_174 --id high_five_slap --desc "a high-five slap" --tags high-five,slap,hands
P $S JR_176 --id squelch --desc "wet mud squelch, funny" --tags mud,squelch,funny
P $S JR_178 --id outro_sting --desc "warm outro sting, story over" --tags outro,sting,ending
$L list | grep -c "^[a-z]"
