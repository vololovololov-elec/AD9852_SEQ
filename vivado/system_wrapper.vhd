-- Copyright 1986-2019 Xilinx, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2019.2 (win64) Build 2708876 Wed Nov  6 21:40:23 MST 2019
-- Date        : Fri Jun  4 15:57:35 2021
-- Host        : e6510-electro running 64-bit major release  (build 9200)
-- Command     : write_vhdl D:/Xilinx/somoa/tmp/system_wrapper.vhd -mode pin_planning -force
-- Design      : system_wrapper
-- Purpose     : Stub declaration of top-level module interface
-- Device      : xc7z010clg400-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_ARITH.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

---- Uncomment the following library declaration if instantiating
---- any Xilinx primitives in this code.
--library UNISIM;
--use UNISIM.VComponents.all;


entity system_wrapper is
  Port ( 
    led_o : out STD_LOGIC_VECTOR ( 7 downto 0 );
    csb2 : out STD_LOGIC;
    fsk1 : out STD_LOGIC;
    sdio_2 : out STD_LOGIC;
    sdio_1 : out STD_LOGIC;
    csb1 : out STD_LOGIC;
    fsk2 : out STD_LOGIC;
    DDR_dqs_p : inout STD_LOGIC_VECTOR ( 3 downto 0 );
    DDR_dm : inout STD_LOGIC_VECTOR ( 3 downto 0 );
    DDR_addr : inout STD_LOGIC_VECTOR ( 14 downto 0 );
    DDR_ba : inout STD_LOGIC_VECTOR ( 2 downto 0 );
    DDR_dq : inout STD_LOGIC_VECTOR ( 31 downto 0 );
    DDR_dqs_n : inout STD_LOGIC_VECTOR ( 3 downto 0 );
    DDR_cas_n : inout STD_LOGIC;
    DDR_ck_n : inout STD_LOGIC;
    DDR_ck_p : inout STD_LOGIC;
    DDR_cke : inout STD_LOGIC;
    DDR_cs_n : inout STD_LOGIC;
    DDR_odt : inout STD_LOGIC;
    DDR_ras_n : inout STD_LOGIC;
    DDR_reset_n : inout STD_LOGIC;
    DDR_we_n : inout STD_LOGIC;
    reset1 : out STD_LOGIC_VECTOR ( 0 downto 0 );
    FIXED_IO_mio : inout STD_LOGIC_VECTOR ( 53 downto 0 );
    FIXED_IO_ddr_vrn : inout STD_LOGIC;
    FIXED_IO_ddr_vrp : inout STD_LOGIC;
    FIXED_IO_ps_clk : inout STD_LOGIC;
    FIXED_IO_ps_porb : inout STD_LOGIC;
    FIXED_IO_ps_srstb : inout STD_LOGIC;
    pclk_p : in STD_LOGIC;
    TXB1 : out STD_LOGIC_VECTOR ( 0 downto 0 );
    ttl_in2 : in STD_LOGIC;
    ttl_in1 : in STD_LOGIC;
    TXB2 : out STD_LOGIC_VECTOR ( 0 downto 0 );
    pclk_n : out STD_LOGIC;
    sclk1 : out STD_LOGIC;
    reset2 : out STD_LOGIC_VECTOR ( 0 downto 0 );
    sclk2 : out STD_LOGIC;
    updt1 : out STD_LOGIC_VECTOR ( 0 downto 0 );
    updt2 : out STD_LOGIC_VECTOR ( 0 downto 0 )
  );

end system_wrapper;

architecture Behavioral of system_wrapper is 
begin

end Behavioral;
