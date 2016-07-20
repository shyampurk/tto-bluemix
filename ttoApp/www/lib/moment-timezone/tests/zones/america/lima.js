"use strict";

var helpers = require("../../helpers/helpers");

exports["America/Lima"] = {
	"guess" : helpers.makeTestGuess("America/Lima", { offset: true, abbr: true }),

	"1908" : helpers.makeTestYear("America/Lima", [
		["1908-07-28T05:08:35+00:00", "23:59:59", "LMT", 18516 / 60],
		["1908-07-28T05:08:36+00:00", "00:08:36", "PET", 300]
	]),

	"1938" : helpers.makeTestYear("America/Lima", [
		["1938-01-01T04:59:59+00:00", "23:59:59", "PET", 300],
		["1938-01-01T05:00:00+00:00", "01:00:00", "PEST", 240],
		["1938-04-01T03:59:59+00:00", "23:59:59", "PEST", 240],
		["1938-04-01T04:00:00+00:00", "23:00:00", "PET", 300],
		["1938-09-25T04:59:59+00:00", "23:59:59", "PET", 300],
		["1938-09-25T05:00:00+00:00", "01:00:00", "PEST", 240]
	]),

	"1939" : helpers.makeTestYear("America/Lima", [
		["1939-03-26T03:59:59+00:00", "23:59:59", "PEST", 240],
		["1939-03-26T04:00:00+00:00", "23:00:00", "PET", 300],
		["1939-09-24T04:59:59+00:00", "23:59:59", "PET", 300],
		["1939-09-24T05:00:00+00:00", "01:00:00", "PEST", 240]
	]),

	"1940" : helpers.makeTestYear("America/Lima", [
		["1940-03-24T03:59:59+00:00", "23:59:59", "PEST", 240],
		["1940-03-24T04:00:00+00:00", "23:00:00", "PET", 300]
	]),

	"1986" : helpers.makeTestYear("America/Lima", [
		["1986-01-01T04:59:59+00:00", "23:59:59", "PET", 300],
		["1986-01-01T05:00:00+00:00", "01:00:00", "PEST", 240],
		["1986-04-01T03:59:59+00:00", "23:59:59", "PEST", 240],
		["1986-04-01T04:00:00+00:00", "23:00:00", "PET", 300]
	]),

	"1987" : helpers.makeTestYear("America/Lima", [
		["1987-01-01T04:59:59+00:00", "23:59:59", "PET", 300],
		["1987-01-01T05:00:00+00:00", "01:00:00", "PEST", 240],
		["1987-04-01T03:59:59+00:00", "23:59:59", "PEST", 240],
		["1987-04-01T04:00:00+00:00", "23:00:00", "PET", 300]
	]),

	"1990" : helpers.makeTestYear("America/Lima", [
		["1990-01-01T04:59:59+00:00", "23:59:59", "PET", 300],
		["1990-01-01T05:00:00+00:00", "01:00:00", "PEST", 240],
		["1990-04-01T03:59:59+00:00", "23:59:59", "PEST", 240],
		["1990-04-01T04:00:00+00:00", "23:00:00", "PET", 300]
	]),

	"1994" : helpers.makeTestYear("America/Lima", [
		["1994-01-01T04:59:59+00:00", "23:59:59", "PET", 300],
		["1994-01-01T05:00:00+00:00", "01:00:00", "PEST", 240],
		["1994-04-01T03:59:59+00:00", "23:59:59", "PEST", 240],
		["1994-04-01T04:00:00+00:00", "23:00:00", "PET", 300]
	])
};