"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
var __rest = (this && this.__rest) || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) if (e.indexOf(p[i]) < 0)
            t[p[i]] = s[p[i]];
    return t;
};
exports.__esModule = true;
var Discord = require("discord.js");
var fs_1 = require("fs");
var index_1 = require("../index");
var commandArgumentError_1 = require("../errors/commandArgumentError");
require("minimist");
var minimist_1 = require("minimist");
var commandInvokeError_1 = require("../errors/commandInvokeError");
var errorHandler_1 = require("./errorHandler");
var commandError_1 = require("../errors/commandError");
var ParameterType;
(function (ParameterType) {
    ParameterType["String"] = "string";
    ParameterType["Number"] = "number";
    ParameterType["Member"] = "member";
    ParameterType["Channel"] = "channel";
    ParameterType["Role"] = "role";
    ParameterType["Emoji"] = "emoji";
})(ParameterType = exports.ParameterType || (exports.ParameterType = {}));
var CommandHandler = /** @class */ (function () {
    function CommandHandler() {
    }
    CommandHandler.reloadCommands = function () {
        var commandModules = fs_1.readdirSync('./bin/commands');
        commandModules.forEach(function (commandModule) {
            var command = require("../commands/" + commandModule).command;
            if (command == undefined) {
                throw new Error("Error loading command " + commandModule + "!");
            }
            CommandHandler.commands.set(command.names, command);
        });
    };
    CommandHandler.parseCommand = function (message) {
        return __awaiter(this, void 0, void 0, function () {
            var content, prefix, regex, match, splitted, s, args, _, optArgs, reqArgs, commandName, command, context, error_1;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        content = message.content;
                        prefix = process.env.PREFIX;
                        if (!content.trim().startsWith(prefix)) {
                            return [2 /*return*/];
                        }
                        regex = /(-\w*\s"+.+?"+|-\w*\s[^"]\S*|[^"]\S*|"+.+?"+)\s*/g // argument matching regex https://regex101.com/r/PbjRv6/1
                        ;
                        match = regex.exec(message.content);
                        splitted = [];
                        while (match != null) {
                            s = match[1].trim();
                            if (s.charAt(0) === '"' && s.charAt(s.length - 1) === '"') {
                                s = s.slice(1, s.length - 1);
                            }
                            splitted.push(s);
                            match = regex.exec(message.content);
                        }
                        splitted = splitted.filter(function (x) { return x !== ''; });
                        args = minimist_1["default"](splitted);
                        console.log(args);
                        _ = args._, optArgs = __rest(args, ["_"]);
                        reqArgs = _;
                        commandName = reqArgs[0].replace(prefix, "");
                        reqArgs = reqArgs.slice(1);
                        command = CommandHandler.commands.find(function (v, k) { return k.includes(commandName); });
                        context = __assign({ command: command }, message);
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        console.log("hewwo");
                        return [4 /*yield*/, this.invokeCommand(context, command, reqArgs, optArgs)];
                    case 2:
                        _a.sent();
                        return [3 /*break*/, 4];
                    case 3:
                        error_1 = _a.sent();
                        if (error_1 instanceof commandError_1["default"])
                            errorHandler_1["default"](error_1);
                        else {
                            throw error_1;
                        }
                        return [3 /*break*/, 4];
                    case 4: return [2 /*return*/];
                }
            });
        });
    };
    CommandHandler.invokeCommand = function (context, command, requiredArgs, optionalArgs) {
        return __awaiter(this, void 0, void 0, function () {
            var args, detectedArgs, fullParams, _i, _a, optParam, zippedDetectedArgs, i, param, arg, temp, error_2;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        if (context.guild === undefined && !command.allowedInDMs)
                            return [2 /*return*/];
                        args = [] // arguments to spread into target function call
                        ;
                        detectedArgs = requiredArgs;
                        fullParams = command.reqParams.concat(command.optionalParams);
                        // detect which optional parameters were passed,
                        for (_i = 0, _a = command.optionalParams; _i < _a.length; _i++) {
                            optParam = _a[_i];
                            if (optionalArgs[optParam.flag] != undefined) {
                                detectedArgs.push(String(optionalArgs[optParam.flag]).trim());
                            }
                            else {
                                detectedArgs.push(undefined);
                            }
                        }
                        zippedDetectedArgs = [detectedArgs.slice(), fullParams.slice()];
                        for (i = 0; i < zippedDetectedArgs[1].length; i++) {
                            param = zippedDetectedArgs[1][i];
                            // if there are less command arguments than expected, throw an error with the parameter that was unable to be filled
                            if (i >= zippedDetectedArgs[0].length) {
                                throw new commandArgumentError_1.CommandArgumentMissingError(param, context);
                            }
                            arg = zippedDetectedArgs[0][i];
                            if (arg == undefined) {
                                args.push(undefined);
                            }
                            else {
                                temp = void 0;
                                // type conversion into required type
                                switch (param.type) {
                                    case 'string':
                                        args.push(arg); // all variables are already strings
                                        break;
                                    case 'number':
                                        temp = Number(arg);
                                        if (isNaN(temp))
                                            throw new commandArgumentError_1.CommandArgumentTypeError(param, context); // if conversion fails, then argument was not of expected type
                                        else
                                            args.push(temp);
                                        break;
                                    case 'member':
                                        temp = this.getMemberFromString(arg, context);
                                        if (temp == undefined)
                                            throw new commandArgumentError_1.CommandArgumentTypeError(param, context);
                                        else
                                            args.push(temp);
                                        break;
                                    case 'channel':
                                        temp = this.getChannelFromString(arg, context);
                                        if (temp == undefined)
                                            throw new commandArgumentError_1.CommandArgumentTypeError(param, context);
                                        else
                                            args.push(temp);
                                        break;
                                    case 'role':
                                        temp = this.getRoleFromString(arg, context);
                                        if (temp == undefined)
                                            throw new commandArgumentError_1.CommandArgumentTypeError(param, context);
                                        else
                                            args.push(temp);
                                        break;
                                    case 'emoji':
                                        temp = this.getEmojiFromString(arg, context);
                                        if (temp == undefined)
                                            throw new commandArgumentError_1.CommandArgumentTypeError(param, context);
                                        else
                                            args.push(temp);
                                        break;
                                }
                            }
                        }
                        _b.label = 1;
                    case 1:
                        _b.trys.push([1, 3, , 4]);
                        return [4 /*yield*/, command.target.apply(command, [context].concat(args))];
                    case 2:
                        _b.sent();
                        return [3 /*break*/, 4];
                    case 3:
                        error_2 = _b.sent();
                        throw new commandInvokeError_1.CommandInvokeError(error_2, context);
                    case 4: return [2 /*return*/];
                }
            });
        });
    };
    CommandHandler.getMemberFromString = function (text, context) {
        if (!text || typeof text !== 'string' || context.guild == undefined)
            return;
        if (text.startsWith('<@') && text.endsWith('>')) {
            text = text.slice(2, -1);
            if (text.startsWith('!')) {
                text = text.slice(1);
            }
            return context.guild.members.get(text);
        }
        else {
            return context.guild.members.find(function (member) {
                return member.user.username.startsWith(text) || member.nickname.startsWith(text);
            });
        }
    };
    CommandHandler.getChannelFromString = function (text, context) {
        if (!text || typeof text !== 'string' || context.guild == undefined)
            return;
        if (text.startsWith('<#') && text.endsWith('>')) {
            text = text.slice(2, -1);
            return index_1.client.channels.get(text);
        }
        else {
            return context.guild.channels.find(function (channel) {
                return channel.name.startsWith(text);
            });
        }
    };
    CommandHandler.getRoleFromString = function (text, context) {
        if (!text || typeof text !== 'string' || context.guild === undefined)
            return;
        if (text.startsWith('<@&') && text.endsWith('>')) {
            text = text.slice(3, -1);
            return context.guild.roles.get(text);
        }
        else {
            return context.guild.roles.find(function (role) {
                return role.name.startsWith(text);
            });
        }
    };
    CommandHandler.getEmojiFromString = function (text, context) {
        if (!text || typeof text !== 'string' || context.guild === undefined)
            return;
        var regex = /<:[a-zA-Z0-9]+:([0-9]+)>/g;
        var match = regex.exec(text);
        if (match != null) {
            text = match[1];
        }
        return context.guild.emojis.get(text);
    };
    CommandHandler.commands = new Discord.Collection();
    return CommandHandler;
}());
exports["default"] = CommandHandler;
