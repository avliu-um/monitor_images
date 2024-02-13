BLUE='\033[0;34m'
GREY='\033[1;30m'
NC='\033[0m' # No color

echo -e "${BLUE}Welcome to the monitor-images runner!${NC}"
echo -e "${BLUE}------------------------------------------------------------------------------------------------------------${NC}"
echo -e "${BLUE}SETUP${NC}"
while true; do
  echo -e "${BLUE}Please enter the (absolute) filepath of the input directory (where the images are currently stored):${NC}"
  read local_input_dir
  # Check if the directory exists
  if [ -d "$local_input_dir" ]; then
    echo -e "${BLUE}Thank you.${NC}"
    break
  else
    echo -e "${BLUE}Directory does not exist, please enter a valid directory.${NC}"
  fi
done
while true; do
  echo -e "${BLUE}Please enter the (absolute) filepath of the output directory (where you would like the output to be stored):${NC}"
  read local_output_dir
  # Check if the directory exists
  if [ -d "$local_input_dir" ]; then
    echo -e "${BLUE}Thank you.${NC}"
    break
  else
    echo -e "${BLUE}Directory does not exist, please enter a valid directory.${NC}"
  fi
done
echo -e "${BLUE}------------------------------------------------------------------------------------------------------------${NC}"
echo -e "${BLUE}EXECUTION${NC}"
echo -e "${BLUE}Checking for newer versions of code and updating if necessary.${NC}"

docker pull avliu/monitor-images:latest

echo -e "${BLUE}Running the monitor-images process (please leave this terminal open and check back periodically for status)...${NC}"
docker run  \
--platform linux/amd64 \
-v "$local_input_dir":/home/seluser/input \
-v "$local_output_dir":/home/seluser/output \
avliu/monitor-images:latest

echo -e "${BLUE}...Done! Please see output.csv in the output directory for results.${NC}"