echo "Welcome!"

echo "Please enter the (absolute) filepath to the input directory (where the images are stored):"
read local_input_dir
echo "Please enter the (absolute) filepath to the output directory (where the output will be stored):"
read local_output_dir

echo "Running the monitor-images process (please leave this terminal open and check back periodically for status)."

docker run  \
--platform linux/amd64 \
-v "$local_input_dir":/home/seluser/input \
-v "$local_output_dir":/home/seluser/output \
avliu/monitor-images:latest

echo "Done! Please check the output directory for results."