#include <stdio.h>
#include <cuda_runtime.h>
#include <cufft.h>
#include <math.h>
#include <fstream>
#include <arpa/inet.h>
#include <unistd.h>
#include <thread>
#include <vector>

#include <cstdio>
#include <cstdlib>
#include <helper_cuda.h>
#include <helper_string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

#define CHIRP_LEN 256
#define NUM_CHIRPS 128
#define NUM_CHANNELS 4
#define RANGE_SIZE CHIRP_LEN
#define DOPPLER_SIZE NUM_CHIRPS
#define CLIENT_PORT 4095
#define FRAME_SIZE (NUM_CHANNELS * CHIRP_LEN * NUM_CHIRPS)
#define IN_SERVER_PORT 4097
#define IN_SERVER_IP_ADDRESS "192.168.33.28"
#define BUFFER_SIZE 65536
#define NO_OF_FRAMES = 1

#define gpuErrchk(ans) { gpuAssert((ans), __FILE__, __LINE__); }
inline void gpuAssert(cudaError_t code, char *file, int line, bool abort=true)
{
   if (code != cudaSuccess)
   {
      fprintf(stderr,"GPUassert: %s %s %d\n", cudaGetErrorString(code), file, line);
      if (abort) exit(code);
   }
}
int client_sockfd = 0;
struct sockaddr_in out_server_addr;
struct sockaddr_in in_server_addr;



/*
__device__ int g_uids = 0;

__global__ void cdp_kernel(int max_depth, int depth, int thread, int parent_uid)
{
    // We create a unique ID per block. Thread 0 does that and shares the value with the other threads.
    __shared__ int s_uid;

    if (threadIdx.x == 0)
    {
        s_uid = atomicAdd(&g_uids, 1);
    }

    __syncthreads();


    // We print the ID of the block and information about its parent.
    //print_info(depth, thread, s_uid, parent_uid);

    // We launch new blocks if we haven't reached the max_depth yet.
    if (++depth >= max_depth)
    {
        return;
    }

    cdp_kernel<<<gridDim.x, blockDim.x>>>(max_depth, depth, threadIdx.x, s_uid);
}

*/


__global__ void averageChannels(short *input, float2 *output) {
	
	printf("\nEntered Average channels"); 
	
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
	printf("\nCalculating average : %d %d %d %d", idx, blockIdx.x, blockDim.x, threadIdx.x );

    if (idx < CHIRP_LEN * NUM_CHIRPS) {

		        
		float2 sum = {0, 0};
        for (int ch = 0; ch < NUM_CHANNELS; ch++) {
            //sum.x += input[idx + ch * CHIRP_LEN * NUM_CHIRPS].x;
            //sum.y += input[idx + ch * CHIRP_LEN * NUM_CHIRPS].y;
            sum.x += (float)input[idx + ch * CHIRP_LEN * NUM_CHIRPS];
            sum.y += (float)input[idx + ch * CHIRP_LEN * NUM_CHIRPS];
        }
        output[idx].x = sum.x / NUM_CHANNELS;
        output[idx].y = sum.y / NUM_CHANNELS;
		
    }

	//printf(" %f, %f ", output[0].x, output[idx].y);
}

__global__ void applyLogScaling(float *input, float *output, int size) {

    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < size) {
        output[idx] = 10 * log10f(input[idx] + 1e-6);
    }
}

__global__ void computePower(float2 *d_avg, float *d_power) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < CHIRP_LEN * NUM_CHIRPS) {
        d_power[idx] = d_avg[idx].x * d_avg[idx].x + d_avg[idx].y * d_avg[idx].y;
    }
}

void configure_client_socket(){

    client_sockfd = socket(AF_INET, SOCK_STREAM, 0);
    
	if (client_sockfd < 0) {
        perror("\nSocket creation failed");
        return;
    }
	printf("\n Created the socket stream");
    
    out_server_addr.sin_family = AF_INET;
    out_server_addr.sin_port = htons(CLIENT_PORT);
    //out_server_addr.sin_addr.s_addr = inet_addr("192.168.33.29");

	printf("\nConfigured the address and port");

    if (inet_pton(AF_INET, "127.0.0.1", &out_server_addr.sin_addr) <= 0) {
        perror ("Invalid address/ Address not supported");
        return;
    }
    printf("Connecting to the socket ");
	if (connect(client_sockfd, (struct sockaddr*)&out_server_addr, sizeof(out_server_addr)) < 0) {
        perror("\nConnection failed 127.0.0.1 ");
        close(client_sockfd);
        return;
    }
	printf("\n Successfully connected to the client");
}




void close_client_socket(){
	close(client_sockfd);
}

void send_output(float *output, int size) {
	printf("\nSend output Size : %d ", size);

    send(client_sockfd, output, size * sizeof(float), 0);
    
	return;
}



void process_frame(short *h_input, int device_id) {

	printf("Process frame. Device Id : %d", device_id);

    //cudaSetDevice(device_id);
	//cudaDeviceSynchronize();

    short *d_input;
	float2 *d_avg;
    float *d_power, *d_log_power, *d_output;
    float *h_output = new float[CHIRP_LEN * NUM_CHIRPS];
   
	printf("\nAllocating memories. Device Id %d ", device_id);
    gpuErrchk(cudaMalloc((void **)&d_input, FRAME_SIZE * sizeof(short) * 16));
    gpuErrchk(cudaMalloc((void **)&d_avg, CHIRP_LEN * NUM_CHIRPS * sizeof(float2)*16));
    gpuErrchk(cudaMalloc((void **)&d_power, CHIRP_LEN * NUM_CHIRPS * sizeof(float)*8));
    gpuErrchk(cudaMalloc((void **)&d_log_power, CHIRP_LEN * NUM_CHIRPS * sizeof(float)*8));
    gpuErrchk(cudaMalloc((void **)&d_output, CHIRP_LEN * NUM_CHIRPS * sizeof(float)));
  	int size = (int)FRAME_SIZE * sizeof(short)*16;
	printf("\nMemory allocation completed. Copying the input to h_input, Size  %d ", size);
    gpuErrchk(cudaMemcpy(d_input, h_input, size, cudaMemcpyHostToDevice));

	/*
	int i = 0, j = 0;
	int avg_index = 0;
	int base_index, chirp_index, channel_index;
	for ( i = 0; i < NUM_CHIRPS; i++ ){
		//base_index = i * CHIRP_LEN*2*4;				
		for (j = 0 ; j < CHIRP_LEN*2; j=j+2){
			base_index = i * CHIRP_LEN + j;
			d_avg[avg_index].x = d_input[base_index];
			d_avg[avg_index].y = d_input[base_index +1]; 
			printf("%f + j%f", d_avg[avg_index].x, d_avg[avg_index].y);
		}
	}
 	*/
	printf("\nCreating 3 dimensional array");
    
	dim3 blockSize(256);
	//printf("\nCreated 3 dim block");
	int grid_size = (CHIRP_LEN * NUM_CHIRPS + blockSize.x - 1) / blockSize.x;

	//printf("\nGrid size = %d", grid_size);
    dim3 gridSize(grid_size);
	printf("\nPopulating the average of all the channel data ");
    averageChannels<<<gridSize, blockSize>>>(d_input, d_avg);
	gpuErrchk(cudaDeviceSynchronize());

	printf("\nAverages calculated %f %f %f %f", d_avg[0].x, d_avg[0].y, d_avg[1].x, d_avg[1].y);
	printf("\nAverages calculated" );

	if( d_input == NULL || d_avg == NULL)
		printf("\nCalulated the average failed");

	//printf("\nCalculated the average %f %f %f %f", d_avg[0].x,  d_avg[0].y,  d_avg[16].x, d_avg[16].x );  	
	
    cufftHandle plan;
	printf("\nCalculating 2 dim fft. Device id = %d", device_id);
    cufftPlan2d(&plan, CHIRP_LEN, NUM_CHIRPS, CUFFT_C2C);
    cufftExecC2C(plan, d_avg, d_avg, CUFFT_FORWARD);
	
	computePower<<<gridSize, blockSize>>>(d_avg, d_power);

	printf("\nCompleted calculation of 2Dim FFT. Device id =%d", device_id);
	//if ( plan != NULL)
    cufftDestroy(plan);

	//printf("\nComputing the Absolute value. Device Id = %d\n", device_id);

	//checkCudaErrors(cudaGetLastError());
	//computePower<<<gridSize, blockSize>>>(d_avg, d_avg);
	
    printf("\nApplying the logerthemic scaling ");

    applyLogScaling<<<gridSize, blockSize>>>(d_power, d_log_power, CHIRP_LEN * NUM_CHIRPS);

    cudaMemcpy(h_output, d_log_power, CHIRP_LEN * NUM_CHIRPS * sizeof(float), cudaMemcpyDeviceToHost);

	printf("\nSending the output through socket. Device Id : %d. Length = %d", device_id, (CHIRP_LEN * NUM_CHIRPS));
    //send_output(h_output, CHIRP_LEN * NUM_CHIRPS);
	send_output(h_output, CHIRP_LEN * NUM_CHIRPS);
	printf("\nFreeing all the memories");
    cudaFree(d_input);
    cudaFree(d_avg);
    cudaFree(d_power);
    cudaFree(d_log_power);
    cudaFree(d_output);
    delete[] h_output;

}

void configure_server_socket(){
    std::vector<std::thread> threads;
    int device_id = 0;
	int server_fd, new_socket;
	unsigned char buffer[BUFFER_SIZE];
	int i = 0;
	
	socklen_t addrlen = sizeof(in_server_addr);
	int opt = 1;
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }
	printf("\nServer socket created");
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt))) {
        perror("setsockopt");
        close(server_fd);
        exit(EXIT_FAILURE);
    }
	printf("\nServer socket options are set");
    in_server_addr.sin_family = AF_INET;
    in_server_addr.sin_addr.s_addr = inet_addr(IN_SERVER_IP_ADDRESS);
    in_server_addr.sin_port = htons(IN_SERVER_PORT);
	printf("\nServer socket configured. Binding to the ports");

    if (bind(server_fd, (struct sockaddr *)&in_server_addr, sizeof(in_server_addr)) < 0) {
        perror("Bind failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }
	printf("\nBinding to the server socket successful. Listening");

    if (listen(server_fd, 3) < 0) {
        perror("Listen failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

	printf("Server listening on %s:%d\n", IN_SERVER_IP_ADDRESS, IN_SERVER_PORT);
	
    for (i = 0; i < 1; i++ ) {
        // Accept a new connection
        if ((new_socket = accept(server_fd, (struct sockaddr *)&in_server_addr, &addrlen)) < 0) {
            perror("Accept failed");
            continue;
        }
        printf("Connected to client\n");
		int total_frame_bytes = FRAME_SIZE * sizeof(short)*16;
		//short *h_input = new short[FRAME_SIZE*16];
		short *h_input;
		short *d_input = new short[FRAME_SIZE*16];
		int current_pos = 0;
		int packet_size  = 1296 * 16;

    	while (true) {		   
			//int bytes_read = read(new_socket, reinterpret_cast<short*>(h_input), total_frame_bytes);
			
			h_input = new short[packet_size];
			int bytes_read = read(new_socket, h_input, packet_size);
			printf("\nRead %d %d %d %d ", h_input[0], h_input[1], h_input[2], h_input[3]);
			if (bytes_read > 0) {
		        //printf("Received %d bytes of binary data\n", bytes_read);
		        // Echo binary data back to client
		        //send(new_socket, buffer, bytes_read, 0);
				if( current_pos + bytes_read >= total_frame_bytes){
					int delta = total_frame_bytes - current_pos;
					
					printf("\nbytes read = %d, delta = %d", bytes_read, delta);
					printf("\nTotal allocated %d. Total captured %d", total_frame_bytes, (current_pos+bytes_read));
					cudaMemcpy(&d_input[current_pos], h_input, bytes_read, cudaMemcpyHostToDevice);
					break;
				}	
				
				cudaMemcpy(&d_input[current_pos], h_input, bytes_read, cudaMemcpyHostToDevice);
				current_pos = current_pos + bytes_read;
				//printf("Bytes read in this packet = %d. Total bytes read %d", bytes_read, current_pos);
				/*				
				if( current_pos >= total_frame_bytes){
					printf("\nReading of Frame bytes completed. Total read : %d \n", current_pos);
					break;
				} 
				*/
				delete h_input;
				h_input = new short[FRAME_SIZE*16];
		    }else{
				printf("Do not know why bytes are not read. Current size : %d", current_pos);
				break;			
			}

			//break;
		    //process_frame(h_input, device_id);
			//sleep(10);
			//device_id = (device_id + 1) % device_count;

    	}
		delete h_input;
		threads.emplace_back(process_frame, d_input, device_id);
		device_id = device_id + 1; 
        // Read binary data from client
        // Close client socket
        close(new_socket);
    }
    for (auto &t : threads) {
        t.join();
    }
	close_client_socket();
	close(server_fd);
}

int main() {

	int max_depth = 2;
	//cdp_kernel<<<4, 4>>>(max_depth, 0, 0, -1);
    checkCudaErrors(cudaGetLastError());
    int device_count;
    cudaGetDeviceCount(&device_count);
	printf("Maximumn number of devices = %d", device_count);
	

    //std::ifstream file("/home/nvdia/Programs/Services/bin/udp_received_file.bin", std::ios::binary);
	/*	
	std::ifstream file("/home/nvdia/UART_com/test.bin", std::ios::binary);

    if (!file) {
        printf("\n\nError: Unable to open file!\n");
        return -1;
    }*/
	printf("\n File opened ");

    //std::vector<std::thread> threads;
    //int device_id = 0;
	
 	configure_client_socket();
	printf("\nReading the file and pupulating the memory ");
	configure_server_socket();
	/*
    while (true) {
        float2 *h_input = new float2[FRAME_SIZE];
        if (!file.read(reinterpret_cast<char*>(h_input), FRAME_SIZE * sizeof(float2))) {
            delete[] h_input;
            break;
        }
		printf("\nAssigning each frame to a different thread");
        threads.emplace_back(process_frame, h_input, device_id);
		device_id = device_id + 1; 
		break;
        //process_frame(h_input, device_id);
		//sleep(10);
		//device_id = (device_id + 1) % device_count;
    }

    file.close();
	*/

	

	/*
    for (auto &t : threads) {
        t.join();
    }
	close_client_socket();
*/
    return 0;
}


