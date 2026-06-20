`timescale 1ns / 1ps

module display_control_model_tb;

reg [1:0] display_mode;
reg [7:0] threshold;
reg overlay_enable;
reg [23:0] rgb_pixel;
reg [7:0] edge_pixel;
wire [23:0] rgb_out;

display_control_model dut (
    .display_mode(display_mode),
    .threshold(threshold),
    .overlay_enable(overlay_enable),
    .rgb_pixel(rgb_pixel),
    .edge_pixel(edge_pixel),
    .rgb_out(rgb_out)
);

initial begin
    // 指定生成的波形文件名
    $dumpfile("display_control_tb_wave.vcd");
    // 0 表示记录顶层模块及所有子模块的全部信号
    $dumpvars(0, display_control_model_tb);
end

initial begin
    rgb_pixel = 24'h204080;
    edge_pixel = 8'd90;
    threshold = 8'd80;
    overlay_enable = 1'b0;

    display_mode = 2'd0;
    #1;
    if (rgb_out !== 24'h204080) begin
        $fatal(1, "original mode failed: %h", rgb_out);
    end

    display_mode = 2'd1;
    #1;
    if (rgb_out !== 24'h3d3d3d) begin
        $fatal(1, "gray mode failed: %h", rgb_out);
    end

    display_mode = 2'd2;
    #1;
    if (rgb_out !== 24'hffffff) begin
        $fatal(1, "edge mode high threshold failed: %h", rgb_out);
    end

    threshold = 8'd120;
    #1;
    if (rgb_out !== 24'h000000) begin
        $fatal(1, "edge mode low edge failed: %h", rgb_out);
    end

    threshold = 8'd80;
    display_mode = 2'd3;
    #1;
    if (rgb_out !== 24'hff2020) begin
        $fatal(1, "overlay mode failed: %h", rgb_out);
    end

    display_mode = 2'd0;
    overlay_enable = 1'b1;
    #1;
    if (rgb_out !== 24'hff2020) begin
        $fatal(1, "overlay enable failed: %h", rgb_out);
    end

    $display("display_control_model_tb passed");
    $finish;
end

endmodule
