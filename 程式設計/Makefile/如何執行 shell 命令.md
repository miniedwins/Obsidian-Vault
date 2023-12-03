
```
PLATFORM_ID = $$ (uname -a)

.PHONY: test
test:
    @if [ ! -d "$(BUILD_DIR)" ]; then \
        echo "Build your dir"; \
    fi      
        
    @./test.sh;
    
    @echo $(PLATFORM_ID)
```
