# Makefile for CheapShop Java Application

JAVAC=javac
JAVA=java
MAIN=CheapShop
SRC=CheapShop.java

all: $(MAIN).class

$(MAIN).class: $(SRC)
	$(JAVAC) $(SRC)

run: all
	$(JAVA) $(MAIN)

clean:
	del /Q *.class

.PHONY: all run clean 