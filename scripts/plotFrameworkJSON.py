#! /usr/bin/env python

import argparse
import parser
import json

import ROOT
import numpy as np

import CMS_lumi, tdrstyle

ROOT.gROOT.SetBatch(True)

tdrstyle.setTDRStyle()

# kBird palette
stops = np.array([0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 1.0000])
red = np.array([0.2082, 0.0592, 0.0780, 0.0232, 0.1802, 0.5301, 0.8186, 0.9956, 0.9764])
green = np.array([0.1664, 0.3599, 0.5041, 0.6419, 0.7178, 0.7492, 0.7328, 0.7862, 0.9832])
blue = np.array([0.5293, 0.8684, 0.8385, 0.7914, 0.6425, 0.4662, 0.3499, 0.1968, 0.0539])
ROOT.TColor.CreateGradientColorTable(9, stops, red, green, blue, 255, 1)

#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.writeExtraText = 1
CMS_lumi.extraText = "Preliminary"
CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)

iPos = 0
if( iPos==0 ): CMS_lumi.relPosX = 0.12

iPeriod = 0

H_ref = 800; 
W_ref = 800; 
W = W_ref
H  = H_ref

# references for T, B, L, R
T = 0.08*H_ref
B = 0.12*H_ref 
L = 0.12*W_ref
R = 0.12*W_ref

canvas = ROOT.TCanvas('canvas', 'canvas', 50, 50, W, H)
canvas.SetFillColor(0)
canvas.SetBorderMode(0)
canvas.SetFrameFillStyle(0)
canvas.SetFrameBorderMode(0)
canvas.SetLeftMargin( L/W )
canvas.SetRightMargin( R/W )
canvas.SetTopMargin( T/H )
canvas.SetBottomMargin( B/H )
canvas.SetTickx(0)
canvas.SetTicky(0)

parser = argparse.ArgumentParser()
parser.add_argument('file', help='JSON file you want to draw')
parser.add_argument('output', help='Output filename')

args = parser.parse_args()

data = {}
with open(args.file, 'r') as f:
    data = json.load(f)

if data['dimension'] != 2:
    raise Exception("Only 2-d scale-factors / efficiencies are supported")

if 'formula' in data and data['formula']:
    raise Exception("Formula are not supported")

x_min = data['binning']['x'][0]
x_max = data['binning']['x'][-1]
y_min = data['binning']['y'][0]
y_max = data['binning']['y'][-1]

x_binning = np.array(data['binning']['x'])
y_binning = np.array(data['binning']['y'])

n_bins_x = len(data['binning']['x']) - 1
n_bins_y = len(data['binning']['y']) - 1

#matrix = np.zeros((n_bins_x, n_bins_y))
x_data = np.zeros(n_bins_x * n_bins_y)
y_data = np.zeros(n_bins_x * n_bins_y)
weights = np.zeros(n_bins_x * n_bins_y)

weights_matrix = np.zeros((n_bins_x, n_bins_y))
weights_up = np.zeros((n_bins_x, n_bins_y))
weights_down = np.zeros((n_bins_x, n_bins_y))

def getJSONBin(data, bin):
    for bins in data:
        if bins['bin'] == bin:
            return bins['values'] if 'values' in bins else (bins['value'], bins['error_low'], bins['error_high'])


index = 0
for i in range(n_bins_x):
    x_bins = getJSONBin(data['data'], [x_binning[i], x_binning[i + 1]])
    for j in range(n_bins_y):
        value, error_low, error_up = getJSONBin(x_bins, [y_binning[j], y_binning[j + 1]])
        x_data[index] = (x_binning[i] + x_binning[i + 1]) / 2
        y_data[index] = (y_binning[j] + y_binning[j + 1]) / 2
        weights[index] = value
        weights_matrix[i, j] = value
        weights_up[i, j] = error_up
        weights_down[i, j] = error_low
        index += 1

# Swap X and Y
foo = x_binning
x_binning = y_binning
y_binning = foo

foo = x_data
x_data = y_data
y_data = foo

foo = n_bins_x
n_bins_x = n_bins_y
n_bins_y = foo

weights_matrix = weights_matrix.transpose()
weights_up = weights_up.transpose()
weights_down = weights_down.transpose()

# Create plots

plot_2d = ROOT.TH2F("values", ";p_{T} (GeV);#eta", n_bins_x, x_binning, n_bins_y, y_binning)
plot_2d.FillN(len(x_data), x_data, y_data, weights)

plot_x_values = []
plot_y_values = []

for i in range(n_bins_x):
    plot_x_values += [(x_binning[i] + x_binning[i + 1]) / 2]

for i in range(n_bins_y):
    plot_y_values += [(y_binning[i] + y_binning[i + 1]) / 2]

plot_x_values = np.array(plot_x_values)
plot_y_values = np.array(plot_y_values)

data_x_mean = weights_matrix.mean(axis=1)
data_x_error_up_mean = np.sqrt((weights_up ** 2).mean(axis=1))
data_x_error_down_mean = np.sqrt((weights_down ** 2).mean(axis=1))

data_y_mean = weights_matrix.mean(axis=0)
data_y_error_up_mean = np.sqrt((weights_up ** 2).mean(axis=0))
data_y_error_down_mean = np.sqrt((weights_down ** 2).mean(axis=0))

pt_graph = ROOT.TGraphAsymmErrors(len(plot_x_values), plot_x_values, data_x_mean, ROOT.nullptr, ROOT.nullptr, data_x_error_down_mean, data_x_error_up_mean)

eta_graph = ROOT.TGraphAsymmErrors(len(plot_y_values), plot_y_values, data_y_mean, ROOT.nullptr, ROOT.nullptr, data_y_error_down_mean, data_y_error_up_mean)


xAxis = plot_2d.GetXaxis()
xAxis.SetNdivisions(6,5,0)

yAxis = plot_2d.GetYaxis()
yAxis.SetNdivisions(6,5,0)
yAxis.SetTitleOffset(1)

zAxis = plot_2d.GetZaxis()
zAxis.SetLabelSize(0.03)

plot_2d.SetContour(1000)

plot_2d.Draw('colz')

#draw the lumi text on the canvas
CMS_lumi.CMS_lumi(canvas, iPeriod, iPos)

canvas.cd()
canvas.Update()
canvas.RedrawAxis()
frame = canvas.GetFrame()
frame.Draw()

canvas.Print(args.output + '.pdf')

marker_color = ROOT.TColor.GetColor('#542437')
marker_type = 20
marker_size = 2
line_width = 2

pt_graph.SetMarkerStyle(marker_type)
pt_graph.SetMarkerColor(marker_color)
pt_graph.SetMarkerSize(marker_size)
pt_graph.SetLineColor(marker_color)
pt_graph.SetLineWidth(line_width)

pt_graph.Draw("AP")
pt_graph.GetXaxis().SetTitle('p_{T} (GeV)')

CMS_lumi.CMS_lumi(canvas, iPeriod, iPos)

canvas.Print(args.output + '_pt.pdf')

eta_graph.SetMarkerStyle(marker_type)
eta_graph.SetMarkerColor(marker_color)
eta_graph.SetMarkerSize(marker_size)
eta_graph.SetLineColor(marker_color)
eta_graph.SetLineWidth(line_width)

eta_graph.Draw("AP")
eta_graph.GetXaxis().SetTitle('#eta')

CMS_lumi.CMS_lumi(canvas, iPeriod, iPos)

canvas.Print(args.output + '_eta.pdf')
