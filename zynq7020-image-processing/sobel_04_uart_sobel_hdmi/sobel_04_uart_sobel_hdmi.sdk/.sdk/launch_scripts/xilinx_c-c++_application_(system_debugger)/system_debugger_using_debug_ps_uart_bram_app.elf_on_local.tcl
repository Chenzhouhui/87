connect -url tcp:127.0.0.1:3121
source C:/Users/Lenovo/Desktop/zynq7020-image-processing/sobel_04_uart_sobel_hdmi/sobel_04_uart_sobel_hdmi.sdk/top_hw_platform_0/ps7_init.tcl
targets -set -nocase -filter {name =~"APU*" && jtag_cable_name =~ "Digilent JTAG-HS1 210512180081"} -index 0
loadhw -hw C:/Users/Lenovo/Desktop/zynq7020-image-processing/sobel_04_uart_sobel_hdmi/sobel_04_uart_sobel_hdmi.sdk/top_hw_platform_0/system.hdf -mem-ranges [list {0x40000000 0xbfffffff}]
configparams force-mem-access 1
targets -set -nocase -filter {name =~"APU*" && jtag_cable_name =~ "Digilent JTAG-HS1 210512180081"} -index 0
stop
ps7_init
ps7_post_config
targets -set -nocase -filter {name =~ "ARM*#0" && jtag_cable_name =~ "Digilent JTAG-HS1 210512180081"} -index 0
rst -processor
targets -set -nocase -filter {name =~ "ARM*#0" && jtag_cable_name =~ "Digilent JTAG-HS1 210512180081"} -index 0
dow C:/Users/Lenovo/Desktop/zynq7020-image-processing/sobel_04_uart_sobel_hdmi/sobel_04_uart_sobel_hdmi.sdk/ps_uart_bram_app/Debug/ps_uart_bram_app.elf
configparams force-mem-access 0
targets -set -nocase -filter {name =~ "ARM*#0" && jtag_cable_name =~ "Digilent JTAG-HS1 210512180081"} -index 0
con
