CUDA_PATH := /usr/local/cuda

CUDA_HOME := /home/nvdia/cuda/NVIDIA_CUDA-10.2_Samples

NVCC := $(CUDA_PATH)/bin/nvcc

CXX := g++

CXXFLAGS := -std=c++11 -O2

NVCCFLAGS := -arch=sm_60 -O2 --compiler-options '-fPIC'

LDFLAGS := -L$(CUDA_PATH)/lib64 -lcudart -lcufft -lpthread

            LDFLAGS +=  $(TARGET_FS)
            LDFLAGS += -L$(TARGET_FS)/lib
            LDFLAGS += -L$(TARGET_FS)/lib/aarch64-linux-gnu
            LDFLAGS += -L$(TARGET_FS)/usr/lib
            LDFLAGS += -L$(TARGET_FS)/usr/lib/aarch64-linux-gnu

INCLUDE := $(CUDA_HOME)/common/inc/

TARGET := cuda_mmwave_fft

SRC := cuda_mmwave_fft.cu



all: $(TARGET)



$(TARGET): $(SRC)

	$(NVCC) $(NVCCFLAGS) $(SRC) -I $(INCLUDE) -o $(TARGET) $(LDFLAGS)



clean:

	rm -f $(TARGET)


