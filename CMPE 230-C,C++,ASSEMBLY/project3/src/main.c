/**
 * @file main.c
 * @brief Witcher Tracker Project  
 *
 * This program implements an inventory and bestiary tracking system
 * for a fictional Witcher scenario, handling commands like "Geralt loots",
 * "Geralt brews", "Geralt learns", "Geralt trades", etc.
 * It interprets lines of input according to grammar rules and
 * updates or queries internal state (ingredients, potions, trophies, bestiary).
 *
 * @author 
 *   - Ali Ayhan Gunder - Yunus Emre Ozturk
 * @date 14/04/2025
 */
//-------------------------------------------------------------------------------------------------
 #include <stdio.h>
 #include <stdlib.h>
 #include <string.h>
 #include <stddef.h>

 
 /**
  * @brief Checks if a character is an alphabetical ASCII letter.
  * @param c Character to be tested.
  * @return Non-zero if c is A-Z or a-z; 0 otherwise.
  */
 static int my_isalpha(char c) {
     return ((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z'));
 }
 
 /**
  * @brief Checks if a character is considered whitespace .
  *
  * @param c Character to be tested.
  * @return Non-zero if c is one of [space, tab, newline, carriage return, form feed, vertical tab]; 0 otherwise.
  */
 static int my_isspace(char c) {
     return (c == ' '  || c == '\t' || c == '\n' || c == '\r' || c == '\f' || c == '\v');
 }
 //--------------------------------------------------------------
 #define MAX_INGREDIENTS 100
 #define MAX_POTIONS     100
 #define MAX_TROPHIES    100
 #define MAX_BESTIARY    100
 #define MAX_FORMULAS    100
 //--------------------------------------------------------------
 /**
  * @brief Structure representing an ingredient in the Witcher world.
  *
  * @var name     Name of the ingredient.
  * @var quantity Amount of the ingredient in inventory.
  */
 typedef struct {
     char name[50];
     int quantity;
 } Ingredient;
 
 /**
  * @brief Structure representing a potion in the Witcher world.
  *
  * @var name     Name of the potion.
  * @var quantity How many of that potion in inventory.
  */
 typedef struct {
     char name[50];
     int quantity;
 } Potion;
 
 /**
  * @brief Structure representing a monster trophy in the Witcher world.
  *
  * @var monster  Name of the monster that trophy belongs to.
  * @var quantity How many trophies of that monster in inventory.
  */
 typedef struct {
     char monster[50];
     int quantity;
 } Trophy;
 
 /**
  * @brief Structure representing a bestiary entry for a monster.
  *
  * Each monster can have up to 10 effective potions and 10 effective signs known.
  *
  * @var name              Name of the monster.
  * @var effective_potions Array storing names of effective potions(up to 10).
  * @var effective_signs   Array storing names of effective signs(up to 10).
  * @var potion_count      Number of known effective potions for this monster.
  * @var sign_count        Number of known effective signs for this monster.
  */
 typedef struct {
     char name[50];
     char effective_potions[10][50];
     char effective_signs[10][50];
     int potion_count;
     int sign_count;
 } MonsterEntry;
 
 /**
  * @brief Structure representing a potion formula.
  *
  * Each formula can have up to 10 required ingredients.
  *
  * @var potion_name Name of the potion.
  * @var required    Array of ingredients required to brew the potion.
  * @var count       Number of distinct ingredients required.
  */
 typedef struct {
     char potion_name[50];
     Ingredient required[10];
     int count;
 } PotionFormula;
 
 /* ------------------- Global Arrays ------------------- */
 
 /** Global array storing all known ingredients. */
 Ingredient ingredients_inventory[MAX_INGREDIENTS];
 /** Number of valid entries in ingredients_inventory. */
 int ingredient_count = 0;
 
 /** Global array storing all known potions in inventory. */
 Potion potions_inventory[MAX_POTIONS];
 /** Number of valid entries in potions_inventory. */
 int potion_count = 0;
 
 /** Global array storing all monster trophies in inventory. */
 Trophy trophies_inventory[MAX_TROPHIES];
 /** Number of valid entries in trophies_inventory. */
 int trophy_count = 0;
 
 /** Global array storing bestiary info for monsters. */
 MonsterEntry bestiary[MAX_BESTIARY];
 /** Number of valid entries in bestiary. */
 int bestiary_count = 0;
 
 /** Global array storing known potion formulas. */
 PotionFormula formulas[MAX_FORMULAS];
 /** Number of valid entries in formulas. */
 int formula_count = 0;
 
 /**
  * @brief Trims leading and trailing whitespace from a C string.
  *
  * Uses @c my_isspace , this modifies the string in-place.
  *
  * @param str Pointer to the string to be trimmed.
  * @return Pointer to the trimmed string (which is still @p str).
  */
 char* trim(char* str) {
     while (*str && my_isspace(*str)) {
         str++;
     }
     if (*str == '\0') return str; // fully whitespace or empty
 
     char *end = str + strlen(str) - 1;
     while (end > str && my_isspace(*end)) {
         *end = '\0';
         end--;
     }
     return str;
 }
 
 /**
  * @brief Removes the '?' from a query and trims.
  *
  * @param str Pointer to the string.
  * @return Pointer to trimmed string with '?' removed if it existed.
  */
 char* remove_question_mark(char* str) {
     char* qmark = strchr(str, '?');
     if (qmark) {
         *qmark = '\0';
     }
     return trim(str);
 }
 
 /* ------------------- Basic Inventory Operations --------------------- */
 
 /**
  * @brief Adds an ingredient to inventory or increases its quantity if already present.
  *
  * @param name Name of the ingredient .
  * @param qty  How many units to add.
  */
 void add_ingredient(const char* name, int qty) {
     for (int i = 0; i < ingredient_count; i++) {
         if (strcmp(ingredients_inventory[i].name, name) == 0) {
             ingredients_inventory[i].quantity += qty;
             return;
         }
     }
     strcpy(ingredients_inventory[ingredient_count].name, name);
     ingredients_inventory[ingredient_count].quantity = qty;
     ingredient_count++;
 }
 
 /**
  * @brief Retrieves how many of an ingredient Geralt has.
  *
  * @param name Name of  the ingredient.
  * @return Quantity, or 0 if not found.
  */
 int get_ingredient_quantity(const char* name) {
     for (int i = 0; i < ingredient_count; i++) {
         if (strcmp(ingredients_inventory[i].name, name) == 0) {
             return ingredients_inventory[i].quantity;
         }
     }
     return 0;
 }
 
 /**
  * @brief Subtracts a certain quantity of an ingredient from the inventory.
  *
  * @param name Name of the ingredient.
  * @param qty  How many units to subtract.
  * @return 1 if successful, 0 if ingredient is insufficient.
  */
 int subtract_ingredient(const char* name, int qty) {
     for (int i = 0; i < ingredient_count; i++) {
         if (strcmp(ingredients_inventory[i].name, name) == 0) {
             if (ingredients_inventory[i].quantity < qty) return 0;
             ingredients_inventory[i].quantity -= qty;
             return 1;
         }
     }
     return 0;
 }
 
 /* ------------------- Potions --- -------------------------- */
 
 /**
  * @brief Validates whether a string is a legal potion name.
  *
  * Legal potion name rules :
  *   - Only alphabetical letters and single spaces in between.
  *   - No consecutive spaces, no numeric or special characters.
  *
  * @param name The potion name candidate.
  * @return 1 if valid, 0 otherwise.
  */
 int is_valid_potion_name(const char* name) {
     if (strlen(name) == 0) return 0;
 
     for (int i = 0; name[i]; i++) {
         if (!(my_isalpha(name[i]) || (name[i] == ' '))) {
             return 0;
         }
         if (i > 0 && name[i] == ' ' && name[i - 1] == ' ') {
             return 0; // disallow consecutive spaces
         }
     }
     return 1;
 }
 
 /**
  * @brief Adds potion to the potions inventory or increases quantity if it exists.
  *
  * @param name Name of the potion.
  * @param qty  How many potions to add.
  */
 void add_potion(const char* name, int qty) {
     for (int i = 0; i < potion_count; i++) {
         if (strcmp(potions_inventory[i].name, name) == 0) {
             potions_inventory[i].quantity += qty;
             return;
         }
     }
     strcpy(potions_inventory[potion_count].name, name);
     potions_inventory[potion_count].quantity = qty;
     potion_count++;
 }
 
 /**
  * @brief Retrieves how many of  certain potion Geralt has in inventory.
  *
  * @param name Name of the potion.
  * @return Quantity of the potion, or 0 if none.
  */
 int get_potion_quantity(const char* name) {
     for (int i = 0; i < potion_count; i++) {
         if (strcmp(potions_inventory[i].name, name) == 0) {
             return potions_inventory[i].quantity;
         }
     }
     return 0;
 }
 
 /* ------------------- Trophies ----------------------------- */
 
 /**
  * @brief Adds monster trophies to the trophy inventory or increases existing quantity.
  *
  * @param monster Name of the monster trophy.
  * @param qty     How many trophies to add.
  */
 void add_trophy(const char* monster, int qty) {
     for (int i = 0; i < trophy_count; i++) {
         if (strcmp(trophies_inventory[i].monster, monster) == 0) {
             trophies_inventory[i].quantity += qty;
             return;
         }
     }
     strcpy(trophies_inventory[trophy_count].monster, monster);
     trophies_inventory[trophy_count].quantity = qty;
     trophy_count++;
 }
 
 /**
  * @brief Removes a certain number of monster trophy from the inventory.
  *
  * @param monster Which monster's trophy to remove.
  * @param qty     How many to remove.
  * @return 1 if successful, 0 if not enough trophies.
  */
 int remove_trophy(const char* monster, int qty) {
     for (int i = 0; i < trophy_count; i++) {
         if (strcmp(trophies_inventory[i].monster, monster) == 0) {
             if (trophies_inventory[i].quantity < qty) return 0;
             trophies_inventory[i].quantity -= qty;
             return 1;
         }
     }
     return 0;
 }
 
 /**
  * @brief Retrieves how many trophies of particular monster Geralt has.
  *
  * @param monster Monster name.
  * @return Number of trophies, or 0 if not present.
  */
 int get_trophy_quantity(const char* monster) {
     for (int i = 0; i < trophy_count; i++) {
         if (strcmp(trophies_inventory[i].monster, monster) == 0) {
             return trophies_inventory[i].quantity;
         }
     }
     return 0;
 }
 
 /* ------------------- Parsing Helpers ------------------------- */
 
 /**
  * @brief Parses a comma-separated list of "qty Name" ingredients into a array.
  *
  * @param str String containing ingredient data.
  * @param arr Output array for parsed ingredients.
  * @return Number of ingredients parsed, or -1 if invalid format or any quantity <= 0.
  */
 int parse_ingredient_list(const char* str, Ingredient arr[]) {
     int count = 0;
     char buffer[1024];
     strcpy(buffer, str);
     char *token = strtok(buffer, ",");
 
     while (token != NULL && count < 10) {
         token = trim(token);
         int qty;
         char name[50];
         if (sscanf(token, "%d %49s", &qty, name) != 2 || qty <= 0) {
             return -1;
         }
         arr[count].quantity = qty;
         strcpy(arr[count].name, name);
         count++;
         token = strtok(NULL, ",");
     }
     return count;
 }
 
 /* ------------------- Potion Formulas ------------------------- */
 
 /**
  * @brief Returns the index of the formula for a given potion name, or -1 if not found.
  *
  * @param potion Name of the potion formula to look up.
  * @return Index in the formulas array, or -1 if doesn't exist.
  */
 int find_formula_index(const char* potion) {
     for (int i = 0; i < formula_count; i++) {
         if (strcmp(formulas[i].potion_name, potion) == 0)
             return i;
     }
     return -1;
 }
 
 /**
  * @brief Adds new potion formula to the known formulas, if not already known.
  *
  * @param potion Name of the potion.
  * @param req    Array of required ingredients.
  * @param cnt    How many ingredients in req.
  * @return 1 if formula was newly added, 0 if formula already existed.
  */
 int add_formula(const char* potion, Ingredient req[], int cnt) {
     if (find_formula_index(potion) != -1) {
         return 0;
     }
     strcpy(formulas[formula_count].potion_name, potion);
     formulas[formula_count].count = cnt;
     for (int i = 0; i < cnt; i++) {
         formulas[formula_count].required[i] = req[i];
     }
     formula_count++;
     return 1;
 }
 
 /* ------------------- Bestiary ---------------------------- */
 
 /**
  * @brief Finds the index of a monster in the bestiary, or -1 if unknown.
  *
  * @param monster Name of the monster to look up.
  * @return Index in the bestiary array, or -1 if unknown.
  */
 int find_bestiary_index(const char* monster) {
     for (int i = 0; i < bestiary_count; i++) {
         if (strcmp(bestiary[i].name, monster) == 0)
             return i;
     }
     return -1;
 }
 
 /**
  * @brief Adds a known effective potion or sign to the bestiary for a monster.
  *
  * @param monster Name of the monster.
  * @param type    0 for potion, 1 for sign.
  * @param name    Name of the potion or sign.
  * @return 1 if a new monster was added, 2 if updated an existing monster, -1 if already known.
  */
 int add_effectiveness(const char* monster, int type, const char* name) {
     int idx = find_bestiary_index(monster);
     if (idx == -1) {
         // new bestiary entry
         strcpy(bestiary[bestiary_count].name, monster);
         bestiary[bestiary_count].potion_count = 0;
         bestiary[bestiary_count].sign_count = 0;
         idx = bestiary_count;
         bestiary_count++;
         if (type == 0) {
             strcpy(bestiary[idx].effective_potions[bestiary[idx].potion_count++], name);
         } else {
             strcpy(bestiary[idx].effective_signs[bestiary[idx].sign_count++], name);
         }
         return 1;
     } else {
         // existing entry
         if (type == 0) {
             for (int i = 0; i < bestiary[idx].potion_count; i++) {
                 if (strcmp(bestiary[idx].effective_potions[i], name) == 0) {
                     return -1; 
                     // already known
                 }
             }
             strcpy(bestiary[idx].effective_potions[bestiary[idx].potion_count++], name);
         } else {
             for (int i = 0; i < bestiary[idx].sign_count; i++) {
                 if (strcmp(bestiary[idx].effective_signs[i], name) == 0) {
                     return -1; // already known
                 }
             }
             strcpy(bestiary[idx].effective_signs[bestiary[idx].sign_count++], name);
         }
         return 2;
     }
 }
 
 /* ------------------- Sorting Comparators --------------------- */
 
 /**
  * @brief Comparator for sorting Ingredient by name ascending (A to Z).
  *
  * @param a Pointer to the left element.
  * @param b Pointer to the right element.
  * @return Negative if a < b, 0 if equal, positive if a > b, based on strcmp.
  */
 int cmp_ingredient(const void *a, const void *b) {
     const Ingredient *ia = (const Ingredient *)a;
     const Ingredient *ib = (const Ingredient *)b;
     return strcmp(ia->name, ib->name);
 }
 
 /**
  * @brief Comparator for sorting Ingredient by quantity desc, then by name asc.
  *
  * Used for "What is in <potion>?" queries, which sort required ingredients 
  * by descending quantity. Ties are broken by alphabetical order of name.
  *
  * @param a Pointer to the left element (Ingredient *).
  * @param b Pointer to the right element (Ingredient *).
  * @return Comparison result for qsort.
  */
 int cmp_ingredient_desc(const void *a, const void *b) {
     const Ingredient *ia = (const Ingredient *)a;
     const Ingredient *ib = (const Ingredient *)b;
     // Sort by descending quantity
     if (ia->quantity != ib->quantity) {
         return ib->quantity - ia->quantity; 
     }
     // If tie, alphabetical
     return strcmp(ia->name, ib->name);
 }
 
 /**
  * @brief Comparator for sorting Potion by name ascending.
  *
  * @param a Pointer to left element .
  * @param b Pointer to right element.
  * @return strcmp result for their names.
  */
 int cmp_potion(const void *a, const void *b) {
     const Potion *pa = (const Potion *)a;
     const Potion *pb = (const Potion *)b;
     return strcmp(pa->name, pb->name);
 }
 
 /**
  * @brief Comparator for sorting Trophy by monster name ascending.
  *
  * @param a Pointer to left element.
  * @param b Pointer to right element.
  * @return strcmp result for their monster field.
  */
 int cmp_trophy(const void *a, const void *b) {
     const Trophy *ta = (const Trophy *)a;
     const Trophy *tb = (const Trophy *)b;
     return strcmp(ta->monster, tb->monster);
 }
 
 /* ------------------- Command Interpreter --------------------- */
 
 /**
  * @brief Interprets a single line of input and executes the corresponding action or query.
  *
  * This function implements the core grammar-based logic like:
  *  - Geralt loots <ingredient_list>....
  *
  * If the line does not match any recognized pattern or fails validation, returns -1.
  *
  * @param line The raw input line (e.g., "Geralt loots 5 Rebis").
  * @return 0 if the command was valid (and possibly produced output), -1 if invalid.
  */
 int execute_line(const char *line) {
     char cmd[1024];
     strcpy(cmd, line);
 
     // Remove any trailing newline
     size_t len = strlen(cmd);
     if (len > 0 && cmd[len - 1] == '\n') {
         cmd[len - 1] = '\0';
     }
     
     // --- Geralt loots <ingredient_list>
     if (strncmp(cmd, "Geralt loots ", 13) == 0) {
         const char *rest = cmd + 13;
         Ingredient arr[10];
         int cnt = parse_ingredient_list(rest, arr);
         if (cnt < 0) {
             return -1; // invalid format
         }
         for (int i = 0; i < cnt; i++) {
             add_ingredient(arr[i].name, arr[i].quantity);
         }
         printf("Alchemy ingredients obtained\n");
         return 0;
     }
     // --- Geralt learns ...
     else if (strncmp(cmd, "Geralt learns ", 14) == 0) {
         const char *rest = cmd + 14;
         // 1) Possibly: <potion> potion consists of <ingredient_list>
         char *potion_ptr = strstr(rest, "potion consists of");
         if (potion_ptr != NULL) {
             int name_len = potion_ptr - rest - 1;
             if (name_len <= 0) {
                 return -1;
             }
             char potion_name[50];
             strncpy(potion_name, rest, name_len);
             potion_name[name_len] = '\0';
             if (!is_valid_potion_name(trim(potion_name))) {
                 return -1;
             }
             const char *ing_list = potion_ptr + strlen("potion consists of");
             ing_list = trim((char*)ing_list);
             Ingredient arr[10];
             int cnt = parse_ingredient_list(ing_list, arr);
             if (cnt < 0) {
                 return -1;
             }
             if (find_formula_index(potion_name) != -1) {
                 printf("Already known formula\n");
             } else {
                 add_formula(potion_name, arr, cnt);
                 printf("New alchemy formula obtained: %s\n", potion_name);
             }
             return 0;
         }
 
         // 2) Possibly: <sign> sign is effective against <monster>
         char *sign_ptr       = strstr(rest, "sign is effective against");
         // 3) Possibly: <potion> potion is effective against <monster>
         char *potion_eff_ptr = strstr(rest, "potion is effective against");
 
         if (sign_ptr != NULL) {
             // Format: "Igni sign is effective against Harpy" as example in description
             char sign[50], monster[50];
             if (sscanf(rest, "%49s sign is effective against %49s", sign, monster) != 2) {
                 return -1;
             }
             int res = add_effectiveness(monster, 1, sign);
             if (res == -1) {
                 printf("Already known effectiveness\n");
             } else if (res == 1) {
                 printf("New bestiary entry added: %s\n", monster);
             } else {
                 printf("Bestiary entry updated: %s\n", monster);
             }
             return 0;
         }
         else if (potion_eff_ptr != NULL) {
             // Format: "Swallow potion is effective against Wraith"
             char potion[50], monster[50];
             if (sscanf(rest, "%49s potion is effective against %49s", potion, monster) != 2) {
                 return -1;
             }
             if (!is_valid_potion_name(potion)) {
                 return -1;
             }
             int res = add_effectiveness(monster, 0, potion);
             if (res == -1) {
                 printf("Already known effectiveness\n");
             } else if (res == 1) {
                 printf("New bestiary entry added: %s\n", monster);
             } else {
                 printf("Bestiary entry updated: %s\n", monster);
             }
             return 0;
         } else {
             return -1;
         }
     }
     // --- Geralt brews <potion>
     else if (strncmp(cmd, "Geralt brews ", 13) == 0) {
         const char *potion_name = cmd + 13;
         potion_name = trim((char*)potion_name);
         int idx = find_formula_index(potion_name);
         if (idx == -1) {
             printf("No formula for %s\n", potion_name);
             return 0;
         }
         PotionFormula *pf = &formulas[idx];
         // Check if enough ingredients
         for (int i = 0; i < pf->count; i++) {
             if (get_ingredient_quantity(pf->required[i].name) < pf->required[i].quantity) {
                 printf("Not enough ingredients\n");
                 return 0;
             }
         }
         // Subtract them
         for (int i = 0; i < pf->count; i++) {
             subtract_ingredient(pf->required[i].name, pf->required[i].quantity);
         }
         add_potion(potion_name, 1);
         printf("Alchemy item created: %s\n", potion_name);
         return 0;
     }
     // --- Geralt encounters a <monster>
     else if (strncmp(cmd, "Geralt encounters a ", 20) == 0) {
         const char *monster = cmd + 20;
         monster = trim((char*)monster);
         int idx = find_bestiary_index(monster);
         if (idx == -1 || (bestiary[idx].potion_count == 0 && bestiary[idx].sign_count == 0)) {
             printf("Geralt is unprepared and barely escapes with his life\n");
         } else {
             printf("Geralt defeats %s\n", monster);
             // Consume one of each effective potion
             for (int i = 0; i < bestiary[idx].potion_count; i++) {
                 if (get_potion_quantity(bestiary[idx].effective_potions[i]) > 0) {
                     // decrement potion
                     for (int j = 0; j < potion_count; j++) {
                         if (strcmp(potions_inventory[j].name, bestiary[idx].effective_potions[i]) == 0) {
                             potions_inventory[j].quantity -= 1;
                             break;
                         }
                     }
                 }
             }
             add_trophy(monster, 1);
         }
         return 0;
     }
     // --- Geralt trades <trophy_list> for <ingredient_list>
     else if (strncmp(cmd, "Geralt trades ", 14) == 0) {
         const char *rest = cmd + 14;
         char *for_ptr = strstr(rest, " for ");
         if (for_ptr == NULL) {
             return -1;
         }
         
         char trophy_part[256];
         strncpy(trophy_part, rest, for_ptr - rest);
         trophy_part[for_ptr - rest] = '\0';
         
         const char *ing_part = for_ptr + 5;
         // Parse trophy list
         char trophy_buf[256];
         strcpy(trophy_buf, trophy_part);
         char *token = strtok(trophy_buf, ",");
         int valid = 1;
         Trophy required[10];
         int req_count = 0;
         
         while (token != NULL && req_count < 10) {
             token = trim(token);
             int qty;
             char monster[50], trophy_word[50];
             // e.g. "3 Harpy trophy"
             if (sscanf(token, "%d %49s %49s", &qty, monster, trophy_word) != 3 
                 || qty <= 0 
                 || strcmp(trophy_word, "trophy") != 0) {
                 valid = 0;
                 break;
             }
             required[req_count].quantity = qty;
             strcpy(required[req_count].monster, monster);
             req_count++;
             token = strtok(NULL, ",");
         }
         if (!valid) { return -1;
         }
         
         // Check we have them
         for (int i = 0; i < req_count; i++) {
             if (get_trophy_quantity(required[i].monster) < required[i].quantity) {
                 printf("Not enough trophies\n");
                 return 0;
             }
         }
         // Remove trophies
         for (int i = 0; i < req_count; i++) {
             remove_trophy(required[i].monster, required[i].quantity);
         }
         
         // Now parse ingredient list
         Ingredient ing_arr[10];
         int ing_cnt = parse_ingredient_list(ing_part, ing_arr);
         if (ing_cnt < 0) {
             return -1;
         }
         
         // Add them
         for (int i = 0; i < ing_cnt; i++) {
             add_ingredient(ing_arr[i].name, ing_arr[i].quantity);
         }
         printf("Trade successful\n");
         return 0;
     }
     // ================== Queries ==================
     // --- "Total ingredient?"
     else if (strcmp(cmd, "Total ingredient?") == 0) {
         if (ingredient_count == 0) {
             printf("None\n");
         } else {
             Ingredient temp[100];
             int tempCount = 0;
             for (int i = 0; i < ingredient_count; i++) {
                 if (ingredients_inventory[i].quantity > 0) {
                     temp[tempCount++] = ingredients_inventory[i];
                 }
             }
             if (tempCount == 0) {
                 printf("None\n");
             } else {
                 qsort(temp, tempCount, sizeof(Ingredient), cmp_ingredient);
                 for (int i = 0; i < tempCount; i++) {
                     printf("%d %s", temp[i].quantity, temp[i].name);
                     if (i < tempCount - 1) {
                         printf(", ");
                     }
                 }
                 printf("\n");
             }
         }
         return 0;
     }
     // --- "Total potion?"
     else if (strcmp(cmd, "Total potion?") == 0) {
         if (potion_count == 0) {
             printf("None\n");
         } else {
             Potion temp[100];
             int tempCount = 0;
             for (int i = 0; i < potion_count; i++) {
                 if (potions_inventory[i].quantity > 0) {
                     temp[tempCount++] = potions_inventory[i];
                 }
             }
             if (tempCount == 0) {
                 printf("None\n");
             } else {
                 qsort(temp, tempCount, sizeof(Potion), cmp_potion);
                 for (int i = 0; i < tempCount; i++) {
                     printf("%d %s", temp[i].quantity, temp[i].name);
                     if (i < tempCount - 1) {
                         printf(", ");
                     }
                 }
                 printf("\n");
             }
         }
         return 0;
     }
     // --- "Total potion <potion>?"
     else if (strncmp(cmd, "Total potion ", 13) == 0) {
         const char *rest = cmd + 13;
         char temp[100];
         strcpy(temp, rest);
         char *potion_name = remove_question_mark(temp);
         potion_name = trim(potion_name);
         int qty = get_potion_quantity(potion_name);
         printf("%d\n", qty);
         return 0;
     }
     // --- "Total trophy?"
     else if (strcmp(cmd, "Total trophy?") == 0) {
         if (trophy_count == 0) {
             printf("None\n");
         } else {
             Trophy temp[100];
             int tempCount = 0;
             for (int i = 0; i < trophy_count; i++) {
                 if (trophies_inventory[i].quantity > 0) {
                     temp[tempCount++] = trophies_inventory[i];
                 }
             }
             if (tempCount == 0) {
                 printf("None\n");
             } else {
                 qsort(temp, tempCount, sizeof(Trophy), cmp_trophy);
                 for (int i = 0; i < tempCount; i++) {
                     printf("%d %s", temp[i].quantity, temp[i].monster);
                     if (i < tempCount - 1) {
                         printf(", ");
                     }
                 }
                 printf("\n");
             }
         }
         return 0;
     }
     // --- "Total trophy <monster>?"
     else if (strncmp(cmd, "Total trophy ", 13) == 0) {
         const char *rest = cmd + 13;
         char buffer[100];
         strcpy(buffer, rest);
         char *monster = remove_question_mark(buffer);
         monster = trim(monster);
         int qty = get_trophy_quantity(monster);
         printf("%d\n", qty);
         return 0;
     }
     // --- "What is in <potion>?"
     else if (strncmp(cmd, "What is in ", 11) == 0) {
         const char *rest = cmd + 11;
         char buffer[100];
         strcpy(buffer, rest);
         char *potion_name = remove_question_mark(buffer);
         potion_name = trim(potion_name);
         int idx = find_formula_index(potion_name);
         if (idx == -1) {
             printf("No formula for %s\n", potion_name);
             return 0;
         }
         Ingredient tempArr[10];
         for (int i = 0; i < formulas[idx].count; i++) {
             tempArr[i] = formulas[idx].required[i];
         }
         qsort(tempArr, formulas[idx].count, sizeof(Ingredient), cmp_ingredient_desc);
         for (int i = 0; i < formulas[idx].count; i++) {
             printf("%d %s", tempArr[i].quantity, tempArr[i].name);
             if (i < formulas[idx].count - 1) {
                 printf(", ");
             }
         }
         printf("\n");
         return 0;
     }
     // --- "What is effective against <monster>?"
     else if (strncmp(cmd, "What is effective against ", 26) == 0) {
         const char *rest = cmd + 26;
         char buffer[100];
         strcpy(buffer, rest);
         char *monster = remove_question_mark(buffer);
         monster = trim(monster);
         int idx = find_bestiary_index(monster);
         if (idx == -1) {
             printf("No knowledge of %s\n", monster);
             return 0;
         }
         // Combine potions + signs in alphabetical order
         char combined[20][50];
         int count = 0;
         for (int i = 0; i < bestiary[idx].potion_count; i++) {
             strcpy(combined[count++], bestiary[idx].effective_potions[i]);
         }
         for (int i = 0; i < bestiary[idx].sign_count; i++) {
             strcpy(combined[count++], bestiary[idx].effective_signs[i]);
         }
         if (count == 0) {
             printf("No knowledge of %s\n", monster);
             return 0;
         }
         // simple bubble algo. sort for alphabetical order
         for (int i = 0; i < count - 1; i++) {
             for (int j = i + 1; j < count; j++) {
                 if (strcmp(combined[i], combined[j]) > 0) {
                     char tempStr[50];
                     strcpy(tempStr, combined[i]);
                     strcpy(combined[i], combined[j]);
                     strcpy(combined[j], tempStr);
                 }
             }
         }
         for (int i = 0; i < count; i++) {
             printf("%s", combined[i]);
             if (i < count - 1) {
                 printf(", ");
             }
         }
         printf("\n");
         return 0;
     }
     // No match => INVALID
     return -1;
 }
 // ------------------- Main Function --------------------- */
 /**
  * @brief Main entry point of the Witcher Tracker program.
  *
  * Continuously reads lines from stdin, prompts with ">> ",
  * and processes lines using execute_line().
  * If the user types "Exit", the program ends.
  *
  * @return 0 on normal exit.
  */
 int main(void) {
     char line[1025];
     while (1) {
         printf(">> ");
         fflush(stdout);
         if (fgets(line, sizeof(line), stdin) == NULL) {
             break;
         }
         if (strcmp(line, "Exit\n") == 0) {
             break;
         }
         
         int result = execute_line(line);
         if (result == -1) {
             printf("INVALID\n");
         }
         fflush(stdout);
     }
     return 0;
 }
 