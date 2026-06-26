`timescale 1ns / 1ps

module roberts_core #(
    parameter integer WIDTH  = 128,
    parameter integer HEIGHT = 72
) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        frame_start,
    input  wire        gray_valid,
    input  wire [7:0]  gray,
    input  wire [15:0] gray_x,
    input  wire [15:0] gray_y,
    output reg         edge_valid,
    output reg [7:0]   edge_data,
    output reg [15:0]  edge_x,
    output reg [15:0]  edge_y,
    output reg         edge_frame_done
);

    reg [7:0] line0 [0:WIDTH-1];
    reg [7:0] line1 [0:WIDTH-1];

    reg [7:0] top_left;
    reg [7:0] top_right;
    reg [7:0] bottom_left;
    reg [7:0] bottom_right;
    reg [7:0] prev_row_pixel;
    reg [7:0] prev_col_pixel;

    // Roberts cross kernel uses a 2x2 stencil.
    reg signed [9:0] gx;
    reg signed [9:0] gy;
    reg [9:0] abs_gx;
    reg [9:0] abs_gy;
    reg [10:0] mag;
    reg [15:0] out_x;
    reg [15:0] out_y;
    reg        flush_active;
    reg        flush_bottom_row;
    reg [15:0] flush_x;
    reg [15:0] flush_y;

    integer i;

    always @(posedge clk) begin
        if (!rst_n) begin
            edge_valid      <= 1'b0;
            edge_data       <= 8'd0;
            edge_x          <= 16'd0;
            edge_y          <= 16'd0;
            edge_frame_done <= 1'b0;
            top_left <= 8'd0;
            top_right <= 8'd0;
            bottom_left <= 8'd0;
            bottom_right <= 8'd0;
            prev_row_pixel <= 8'd0;
            prev_col_pixel <= 8'd0;
            gx <= 10'sd0;
            gy <= 10'sd0;
            abs_gx <= 10'd0;
            abs_gy <= 10'd0;
            mag <= 11'd0;
            out_x <= 16'd0;
            out_y <= 16'd0;
            flush_active <= 1'b0;
            flush_bottom_row <= 1'b0;
            flush_x <= 16'd0;
            flush_y <= 16'd0;

            for (i = 0; i < WIDTH; i = i + 1) begin
                line0[i] <= 8'd0;
                line1[i] <= 8'd0;
            end
        end else begin
            edge_valid      <= 1'b0;
            edge_frame_done <= 1'b0;

            if (frame_start) begin
                edge_valid <= 1'b0;
                for (i = 0; i < WIDTH; i = i + 1) begin
                    line0[i] <= 8'd0;
                    line1[i] <= 8'd0;
                end
                top_left <= 8'd0;
                top_right <= 8'd0;
                bottom_left <= 8'd0;
                bottom_right <= 8'd0;
                flush_active <= 1'b0;
                flush_bottom_row <= 1'b0;
                flush_x <= 16'd0;
                flush_y <= 16'd0;
            end

            if (flush_active) begin
                edge_valid <= 1'b1;
                edge_data  <= 8'd0;
                edge_x     <= flush_x;
                edge_y     <= flush_y;

                if (!flush_bottom_row) begin
                    if (flush_y == HEIGHT - 2) begin
                        flush_bottom_row <= 1'b1;
                        flush_x <= 16'd0;
                        flush_y <= HEIGHT - 1;
                    end else begin
                        flush_y <= flush_y + 16'd1;
                    end
                end else begin
                    if (flush_x == WIDTH - 1) begin
                        flush_active <= 1'b0;
                        edge_frame_done <= 1'b1;
                    end else begin
                        flush_x <= flush_x + 16'd1;
                    end
                end
            end

            if (gray_valid) begin
                prev_row_pixel = (gray_y >= 1) ? line1[gray_x] : 8'd0;
                prev_col_pixel = (gray_x >= 1) ? gray : 8'd0;

                if (gray_x == 16'd0) begin
                    top_left = 8'd0;
                    top_right = 8'd0;
                    bottom_left = 8'd0;
                    bottom_right = 8'd0;
                end

                top_left = (gray_y >= 1) ? line0[gray_x] : 8'd0;
                top_right = prev_row_pixel;
                bottom_left = (gray_x >= 1) ? line1[gray_x - 16'd1] : 8'd0;
                bottom_right = gray;

                out_x = (gray_x >= 1) ? (gray_x - 16'd1) : 16'd0;
                out_y = (gray_y >= 1) ? (gray_y - 16'd1) : 16'd0;

                if ((gray_x >= 1) && (gray_y >= 1)) begin
                    // Roberts cross: Gx = top_left - bottom_right
                    //                 Gy = top_right - bottom_left
                    gx = $signed({2'd0, top_left}) - $signed({2'd0, bottom_right});
                    gy = $signed({2'd0, top_right}) - $signed({2'd0, bottom_left});

                    abs_gx = gx[9] ? (~gx + 10'd1) : gx;
                    abs_gy = gy[9] ? (~gy + 10'd1) : gy;
                    mag = abs_gx + abs_gy;

                    edge_data  <= (mag > 11'd255) ? 8'hff : mag[7:0];
                    edge_x     <= out_x;
                    edge_y     <= out_y;
                    edge_valid <= 1'b1;
                end

                if ((gray_x >= 1) && (gray_y >= 1) &&
                    ((out_x == 16'd0) || (out_y == 16'd0) ||
                     (out_x == WIDTH - 1) || (out_y == HEIGHT - 1))) begin
                    edge_data  <= 8'd0;
                    edge_x     <= out_x;
                    edge_y     <= out_y;
                    edge_valid <= 1'b1;
                end

                if ((gray_x == WIDTH - 1) && (gray_y == HEIGHT - 1)) begin
                    flush_active <= 1'b1;
                    flush_bottom_row <= 1'b0;
                    flush_x <= WIDTH - 1;
                    flush_y <= 16'd0;
                end

                line0[gray_x] <= line1[gray_x];
                line1[gray_x] <= gray;

                top_left <= top_right;
                top_right <= bottom_right;
                bottom_left <= bottom_right;
                bottom_right <= gray;
            end
        end
    end

endmodule