`timescale 1ns / 1ps

module display_control_model_tb;

reg [2:0] display_mode;
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
    rgb_pixel = 24'h204080;
    edge_pixel = 8'd90;
    threshold = 8'd80;
    overlay_enable = 1'b0;

    // Test 1: MODE_ORIGINAL (3'd0)
    display_mode = 3'd0; #1;
    if (rgb_out !== 24'h204080)
        $fatal(1, "original mode failed: %h", rgb_out);

    // Test 2: MODE_GRAY (3'd1)
    display_mode = 3'd1; #1;
    if (rgb_out !== 24'h3d3d3d)
        $fatal(1, "gray mode failed: %h", rgb_out);

    // Test 3: MODE_EDGE (3'd2) - Sobel, edge >= threshold -> white
    display_mode = 3'd2; #1;
    if (rgb_out !== 24'hffffff)
        $fatal(1, "sobel edge mode failed: %h", rgb_out);

    // Test 4: MODE_EDGE (3'd2) - edge < threshold -> black
    threshold = 8'd120; #1;
    if (rgb_out !== 24'h000000)
        $fatal(1, "sobel below threshold failed: %h", rgb_out);

    // Test 5: MODE_OVERLAY (3'd3)
    threshold = 8'd80;
    display_mode = 3'd3; #1;
    if (rgb_out !== 24'hff2020)
        $fatal(1, "overlay mode failed: %h", rgb_out);

    // Test 6: MODE_ORIGINAL + overlay_enable
    display_mode = 3'd0;
    overlay_enable = 1'b1; #1;
    if (rgb_out !== 24'hff2020)
        $fatal(1, "overlay enable failed: %h", rgb_out);

    // Test 7: MODE_LAPLACIAN (3'd4) - edge >= threshold -> white
    overlay_enable = 1'b0;
    threshold = 8'd80;
    edge_pixel = 8'd90;
    display_mode = 3'd4; #1;
    if (rgb_out !== 24'hffffff)
        $fatal(1, "laplacian mode failed: %h", rgb_out);

    // Test 8: MODE_LAPLACIAN (3'd4) - edge < threshold -> black
    threshold = 8'd120; #1;
    if (rgb_out !== 24'h000000)
        $fatal(1, "laplacian below threshold failed: %h", rgb_out);

    $display("display_control_model_tb passed (8 tests)");
    $finish;
end

endmodule
