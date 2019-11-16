#!/usr/bin/env python2

import os
import re
import subprocess
import argparse
import commands
import json
import git
import shutil
from datetime import date
from common import *

build_warning_list = []
def warning(msg):
    print_msg_with_color(msg, "red")
    build_warning_list.append(msg)

def print_all_warning():
    if len(build_warning_list) > 0:
        print "\n\n"
        print("=================================")
        print("SDK build with following warning:")
        for w in build_warning_list:
            print_msg_with_color(w, "red")
        print("=================================")
        print "\n\n"


def check_error(code, message):
    if (code != 0):
        print message
        exit(-1)

def ensure_path(path, need_clear=False):
    if (not os.path.exists(path)):
        os.makedirs(path)
    if (need_clear):
        os.system("rm -rf %s/*" % (path, ))

def get_root_path(anchor=".clang-format"):
    path = os.path.abspath(__file__)
    while True:
        path = os.path.dirname(path)
        if (os.path.exists(path + "/" + anchor)):
            return path
        if (path == "/"):
            error("%s not found" % anchor)

def git_clone(dir, git_url, git_branch):
    if (os.path.exists(dir)):
        os.system("rm -rf %s" % (dir))
    os.system("git clone -b %s --single-branch %s %s" %(git_branch, git_url, dir))

def git_comp_repo(dir1, dir2):
    if ((not os.path.exists(dir1)) or (not os.path.exists(dir2))):
        return False
    #os.system("git --git-dir=%s/.git rev-parse HEAD" %(dir1))
    sha1 = subprocess.check_output(["git --git-dir=%s/.git rev-parse HEAD" %(dir1)], shell=True) 
    sha2 = subprocess.check_output(["git --git-dir=%s/.git rev-parse HEAD" %(dir2)], shell=True) 
    return sha1 == sha2

def git_branch_check(path, branch):
    repo = git.Repo(path)
    check_error(repo.bare, "error: fail to get repo.")
    repo.git.checkout(branch)

def git_branch_checkout(path, branch):
    repo = git.Repo(path)
    print ("git path: %s, checkout branch %s" % (path, branch)) 
    repo.git.checkout(branch)

def model_encrypt(build_directory, data_directory, sdk_args, model_path):
    encrypt_model = "%s/../thirdparty/dms-core/thirdparty/resource/mtp_tools/encrypt.py \
            -p %s/../thirdparty/dms-core/thirdparty/resource/mtp_tools/ \
            -i %s \
            -o %s/model.tar -m %s -s %s -e '*'" % (
            build_directory,
            build_directory,
            model_path,
            data_directory,
            "XnKVlc5cDf2gP3Qb",
            sdk_args["sdk_token"]
            )
    print encrypt_model
    os.system(encrypt_model)

def doxygen(gcfg, proj_cfg):

    if(not os.path.exists(proj_cfg["adapter_doc_path"] + "/Doxyfile")):
        print "no doxygen for proj" + proj_cfg["name"]
        return

    # check doc path validity:
    assert os.path.exists(proj_cfg["adapter_api_path"]), "adapter api file not exist"
    assert os.path.exists(gcfg["root_path"] + "/adapter/sample"), "adapter sample file not exist"
    assert os.path.exists(proj_cfg["proj_install_path"]), "proj install path not exist"

    # variable set:
    proj_cfg["proj_doxygen_file_path"] = proj_cfg["adapter_doc_path"] + "/Doxyfile"
    proj_cfg["proj_sample_path"] = gcfg["root_path"] + "/adapter/sample"
    proj_cfg["proj_doc_install_path"] = proj_cfg["proj_install_path"] + "/doc"
    
    # prepare env varible for doxygen:
    os.environ["SDK_API_PATH"]            = proj_cfg["adapter_api_path"]
    os.environ["SDK_DOC_PATH"]            = proj_cfg["adapter_doc_path"]
    os.environ["SDK_SAMPLE_PATH"]         = proj_cfg["proj_sample_path"]
    os.environ["SDK_DOC_INSTALL_PATH"]    = proj_cfg["proj_doc_install_path"]

    cmd = "doxygen %s" % (proj_cfg["proj_doxygen_file_path"])
    print "sdk api generated by: %s" % (cmd)
    os.system(cmd)

    doc_gen_latex_path = proj_cfg["proj_doc_install_path"] + "/latex"
    doc_gen_html_path = proj_cfg["proj_doc_install_path"] + "/html"
    if(os.path.exists(doc_gen_latex_path)):
        print "generating pdf from latex"
        cmd = "cd %s && make >/dev/null && mv %s %s" % (doc_gen_latex_path, doc_gen_latex_path + "/refman.pdf", proj_cfg["proj_doc_install_path"] + "/README.pdf")
        os.system (cmd)

        print "creating link for index.html"
        html_redirct = r"<meta http-equiv='REFRESH' content='0;URL=./html/index.html'>"
        cmd = "cd %s && echo \" %s \"  > README.html" % (proj_cfg["proj_doc_install_path"], html_redirct)
        os.system (cmd)

def calculate_footprint(proj_cfg, cfg):
    rel_files_md5 = get_files_md5(proj_cfg["build_rel_path"])
    
    # get git repo info
    module_commit_sha = []
    module_commit_sha = get_git_module_sha(cfg["root_path"])

    # get model info:
    model_cfg = proj_cfg["model_config"]
    models = {}
    for k, v in model_cfg["dms"].items():
        if ("config_" in k) and ("models" in v):
            models[k.replace("config_", "")] = v["models"]

    restult = {
        'git_sha': module_commit_sha,
        'rel_files_md5': rel_files_md5,
        'models': models,
        'build_cfg': cfg
        #'proj_cfg': proj_cfg,
    }
    write_json(proj_cfg["build_rel_path"] + "/footprint.json", restult)

def get_files_md5(dir):
    files = get_all_files(dir)
    demo_files_md5 = []
    for file in files:
        md5_sum = get_md5_sum(file)
        demo_files_md5.append({
            'file': file,
            'md5_sum': md5_sum
        })
    return demo_files_md5

def get_git_submodules(path):
    if(not os.path.exists(path)):
        print "invalid path %s" %(path)
        return ""

    git_commit_info = commands.getstatusoutput('cd %s && git submodule' % path)

    sub_modules = [item.strip() for item in git_commit_info[1].split('\n') if ("fatal" not in item) and item.strip()]
    result = []
    if len(sub_modules) > 0 :
        for module in sub_modules:
            module_info = module.split(' ')
            commit = module_info[0]
            child_path = module_info[1]
            
            child_path = path + "/" + child_path
            child_result = get_git_submodules(child_path)
            if(len(child_result)>0):
                result.append(child_result)

            result.append({
                'module': child_path,
                'commit': commit,
            })
    return result

def get_git_module_sha(path):
    module_infos = get_git_submodules(path)

    git_info = commands.getstatusoutput('git rev-parse HEAD | xargs git name-rev')
    if(len(git_info) >= 1):
        dms_wrapper_info = git_info[1].split(' ')
        module_infos.append({
            'module': 'dms-wrapper',
            'commit': dms_wrapper_info[0],
        })
    return module_infos

def build_env_set(gcfg, proj_cfg):
    proj_cfg["adapter_doc_path"]          = proj_cfg["adapter_root_path"] + "/doc"
    proj_cfg["adapter_api_path"]          = proj_cfg["adapter_root_path"] + "/include"

    proj_cfg["proj_build_path"]           = ("%s/build-%s-%s-%s-%s" % (gcfg["build_path"], proj_cfg["name"], proj_cfg["platform"], proj_cfg["os"], gcfg["version"]))
    proj_cfg["proj_install_path"]         = ("%s/install-%s-%s-%s-%s" % (gcfg["build_path"], proj_cfg["name"], proj_cfg["platform"], proj_cfg["os"], gcfg["version"]))
    proj_cfg["proj_release_path"]         = ("%s/release-%s-%s" % (gcfg["build_path"], proj_cfg["name"], gcfg["version"]))

    os.environ["SDK_VERSION"]             = gcfg["version"]
    os.environ["SDK_PROJECT"]             = gcfg["project"]


def build_cmake_set(gcfg, proj_cfg):
    cmake_opt = ""

    # set cross-compile:
    cross_compile = (proj_cfg["arch"] != "x86_64")
    if (cross_compile):
        cmake_opt += " -DCMAKE_CROSSCOMPILING=ON "

    # set toolchain:
    if (proj_cfg["cc"] in gcfg["build_config"]["cc"]):
        tc_cfg = gcfg["build_config"]["cc"][proj_cfg["cc"]]
        tc_pfx = tc_cfg["path"] + "/" + tc_cfg["toolchain_prefix"] 
        cmake_opt += (" -DCMAKE_C_COMPILER=%s " % (tc_pfx + tc_cfg["c_compiler"] ))
        cmake_opt += (" -DCMAKE_CXX_COMPILER=%s " % (tc_pfx + tc_cfg["cxx_compiler"] ))
        cmake_opt += (" -DCMAKE_AR=%s " % (tc_pfx + tc_cfg["ar"] ))
        cmake_opt += (" -DCMAKE_RANLIB=%s " % (tc_pfx + tc_cfg["ranlib"] ))
        cmake_opt += (" -DCMAKE_STRIP=%s " % (tc_pfx + tc_cfg["strip"] ))
        cmake_opt += (" -DCMAKE_FIND_ROOT_PATH_MODE_PROGRAM=NEVER ")
        cmake_opt += (" -DCMAKE_FIND_ROOT_PATH_MODE_LIBRARY=BOTH ")
        cmake_opt += (" -DCMAKE_FIND_ROOT_PATH_MODE_INCLUDE=ONLY ")
        cmake_opt += (" -DCMAKE_FIND_ROOT_PATH_MODE_PACKAGE=ONLY ")
    else:
        assert not cross_compile, "Wrong toolchain config: %s" % (proj_cfg["cc"])

    #set system:
    assert "platform" in proj_cfg, "missing project platform config"
    if("android" == proj_cfg["os"]):
        cmake_opt += (" -DCMAKE_SYSTEM_NAME=Linux ")
    else:
        cmake_opt += (" -DCMAKE_SYSTEM_NAME=%s " %(proj_cfg["os"]))
    cmake_opt += (" -DCMAKE_SYSTEM_PROCESSOR=%s " %(proj_cfg["arch"]))
    cmake_opt += (" -DSDK_PLATFORM=%s " %(proj_cfg["platform"]))

    if(cross_compile):
        plt_cfg = gcfg["build_config"]["platform"][proj_cfg["platform"]]
        cmake_opt += (" -DCMAKE_FIND_ROOT_PATH=%s " %(plt_cfg["sysroot"]))
        cmake_opt += (" -DCMAKE_SYSROOT=%s " %(plt_cfg["sysroot"]))

        if (proj_cfg["os"] == "android"):
            assert "android-api" in plt_cfg, "Android API not set !"
            cmake_opt += (" -DCMAKE_CXX_FLAGS='-Werror -Wno-error=unused-command-line-argument -Wno-error=extern-c-compat -Wno-error=format -llog'")
            #cmake_opt += (" -DCMAKE_CXX_FLAGS=-Wno-everything ")

    #set npu:
    if(cross_compile):
        plt_cfg = gcfg["build_config"]["platform"][proj_cfg["platform"]]
        if(plt_cfg["npu"] == "airunner"):
            cmake_opt += (" -DNTP_AIRUNNER=ON ")

    #set hal:
    if ("hal" in proj_cfg):
        cmake_opt += (" -DCUSTOMISE_HAL=%s " %(proj_cfg["hal"]))

    #set opencv:
    if ("opencv" in proj_cfg):
        cmake_opt += (" -DCUSTOMISE_OCV=%s " %(proj_cfg["opencv"]))
        #cmake_opt += (" -DUSE_OPENCV3=ON ")

    if ("opencv-embedded" in proj_cfg):
        cmake_opt += (" -DCUSTOMISE_OCV_EMBEDDED=%s " %(proj_cfg["opencv-embedded"]))

    #set minfer:
    if ("minfer" in proj_cfg):
        minfer_arch=proj_cfg["minfer"].replace("-static", "")
        cmake_opt += (" -DCUSTOMIZE_MINFER_ARCH=%s " % (minfer_arch))

        if("-static" in proj_cfg["minfer"]):
            cmake_opt += (" -DSTATIC_LINK_MINFER=1 ")

        if(("cuda" not in proj_cfg["minfer"])): # minfer is very funny here
            cmake_opt += (" -DCPU_ONLY=ON ")

        if (os.path.exists(proj_cfg["minfer_path"])):
            minfer_lib_dir = "%s/lib/%s" %(proj_cfg["minfer_path"], proj_cfg["minfer"])
            assert os.path.exists(minfer_lib_dir), ("wrong minfer lib path : %s" % minfer_lib_dir) 
            proj_cfg["minfer_lib_dir"] = minfer_lib_dir
            cmake_opt += (" -DMINFER_LIB_DIR=%s " %(minfer_lib_dir))

    #set test:
    if (gcfg["build_test"]):
        cmake_opt += (" -DBUILD_TEST=ON ")

    #set sample:
    if (gcfg["build_sample"]):
        cmake_opt += (" -DBUILD_SAMPLE=ON ")

    #set feature:
    if "feature" in proj_cfg:
        for f in proj_cfg["feature"]:
            cmake_opt += (" -DBUILD_FEATURE_%s=ON " % (f))

    #set token:
    if (gcfg["token"]):
        cmake_opt += (" -DSDK_TOKEN=%s " % (gcfg["token"]))

    #set version:
    if (gcfg["version"]):
        cmake_opt += (" -DSDK_VERSION=%s " % (gcfg["version"]))

    if (gcfg["version_extra"]):
        cmake_opt += (" -DSDK_VERSION_EXTRA=%s " % (gcfg["version_extra"]))

    #set project:
    if (gcfg["project"]):
        cmake_opt += (" -DSDK_PROJECT=%s " % (gcfg["project"]))

    #set profile:
    if (gcfg["profile_time"]):
        cmake_opt += (" -DCALIB_TIME=ON " )

    #set gcov:
    if (gcfg["gcov"]):
        cmake_opt += (" -DCODE_COVERAGE=ON " )

    #set cppcheck:
    if (gcfg["cppcheck"]):
        cmake_opt += (" -DCPPCHECK=ON " )
        cmake_opt += (" -DCMAKE_EXPORT_COMPILE_COMMANDS=ON " )

    #set debug:
    if (gcfg["debug"]):
        cmake_opt += (" -DCMAKE_BUILD_TYPE=Debug " )
        cmake_opt += (" -DDEBUG=ON " )
    else:
        cmake_opt += (" -DCMAKE_BUILD_TYPE=Release " )

    #set install path:
    cmake_opt += (" -DCMAKE_INSTALL_PREFIX=%s " % (proj_cfg["proj_install_path"]))

    proj_cfg["cmake_opt"] = cmake_opt

def build_minfer_set(gcfg, proj_cfg):
    proj_cfg["minfer_path"] = gcfg["root_path"] + "/thirdparty/dms-core/thirdparty/minfer-release"
    assert os.path.exists(proj_cfg["minfer_path"]), "minfer path not exist: %s " %(proj_cfg["minfer_path"])

    proj_cfg["minfer_branch"]="master"

    plt_cfg = gcfg["build_config"]["platform"][proj_cfg["platform"]]
    if(plt_cfg["npu"] == "airunner"):
        proj_cfg["minfer_branch"]="wjw/airunner"
    
    print "Switching minfer for a new platform, please wait ..."
    repo = git.Repo(proj_cfg["minfer_path"])

    print ("git path: %s, checkout & pull branch %s" % (proj_cfg["minfer_path"], proj_cfg["minfer_branch"])) 
    repo.git.checkout(proj_cfg["minfer_branch"])
    repo.remotes.origin.pull()
    if("minfer_git_sha" in proj_cfg):
        print_msg_with_color("using a target SHA to checkout minfer", "blue")
        repo.git.checkout(proj_cfg["minfer_git_sha"])

def build_proj(gcfg, proj_cfg):
    # clear directory:
    assert "proj_build_path" in proj_cfg, "proj_build_path not set yet"
    if(gcfg["ib"]):
        print "running incremental build"
        ensure_path(proj_cfg["proj_build_path"], False)
    else:
        print "running clean build"
        ensure_path(proj_cfg["proj_build_path"], True)

    # cmake:
    print "build in [%s]" % (proj_cfg["proj_build_path"], )
    os.chdir(proj_cfg["proj_build_path"])
    cmake_cmd = ("cmake -B%s -H%s %s" %(proj_cfg["proj_build_path"], gcfg["root_path"], proj_cfg["cmake_opt"]))
    print "cmake cmd: ", cmake_cmd

    ret = os.system(cmake_cmd)
    check_error(ret, "error: fail to mkenv.")

    # make:
    if(gcfg["verbose"]):
        ret = os.system("make -j`nproc` VERBOSE=1 install")
    else: 
        ret = os.system("make -j`nproc` install")

    # record build config:
    compile_cmd_path = proj_cfg["proj_build_path"] + "/compile_commands.json"
    if(os.path.exists(compile_cmd_path)):
        proj_cfg["compile_commands"] = read_json(compile_cmd_path)

    check_error(ret, "error: fail to make install")

def strip_lib(gcfg, proj_cfg):
    cross_compile = (proj_cfg["arch"] != "x86_64")
    if(cross_compile):
        tc_cfg = gcfg["build_config"]["cc"][proj_cfg["cc"]]
        tc_pfx = tc_cfg["path"] + "/" + tc_cfg["toolchain_prefix"] 
        strip_tool = tc_pfx + tc_cfg["strip"]
    else:
        strip_tool = "strip"

    for subdir, dirs, files in os.walk(proj_cfg["proj_install_path"] + "/lib"):
        for file in files:
            filepath = subdir + os.sep + file
            cmd = strip_tool + " " + filepath
            print cmd
            ret = os.system(cmd)

def strip_test(gcfg, proj_cfg):
    if(not gcfg["build_test"]):
        return

    cross_compile = (proj_cfg["arch"] != "x86_64")
    if(cross_compile):
        tc_cfg = gcfg["build_config"]["cc"][proj_cfg["cc"]]
        tc_pfx = tc_cfg["path"] + "/" + tc_cfg["toolchain_prefix"] 
        strip_tool = tc_pfx + tc_cfg["strip"]
    else:
        strip_tool = "strip"

    for subdir, dirs, files in os.walk(proj_cfg["proj_install_path"] + "/test"):
        for file in files:
            filepath = subdir + os.sep + file
            cmd = strip_tool + " " + filepath
            print cmd
            ret = os.system(cmd)

def strip_sample(gcfg, proj_cfg):
    if(not gcfg["build_sample"]):
        return

    cross_compile = (proj_cfg["arch"] != "x86_64")
    if(cross_compile):
        tc_cfg = gcfg["build_config"]["cc"][proj_cfg["cc"]]
        tc_pfx = tc_cfg["path"] + "/" + tc_cfg["toolchain_prefix"] 
        strip_tool = tc_pfx + tc_cfg["strip"]
    else:
        strip_tool = "strip"

    for subdir, dirs, files in os.walk(proj_cfg["proj_install_path"] + "/sample"):
        for file in files:
            filepath = subdir + os.sep + file
            cmd = strip_tool + " " + filepath
            print cmd
            ret = os.system(cmd)

def build_model(gcfg, proj_cfg):
    pack_script = gcfg["root_path"] + "/.ci/model_pack.py"
    process_script = gcfg["root_path"] + "/.ci/model_process.py"
    assert os.path.exists(pack_script) and os.path.exists(process_script) , "model pack/process script not exist!!"

    pack_cmd = pack_script + " "
    process_cmd = process_script + " "
    
    # select model_path
    pack_cmd += " --config_path=%s " % (proj_cfg["model_config_path"])
    pack_cmd += " --model_path=%s " % (proj_cfg["model_pool_path"])

    # select model srlz
    if(not gcfg["no_srlz_model"]):
        # get minfer version
        minfer_v = ""
        minfer_v2_h = proj_cfg["minfer_path"] + "/include/minfer_v2.h"
        f = open(minfer_v2_h)
        line = f.readline()
        while line:
            if "MINFER_VERSION_MAJOR" in line:
                minfer_v = minfer_v + line[-2] + "."
            if "MINFER_VERSION_MINOR" in line:
                minfer_v = minfer_v + line[-2] + "."
            if "MINFER_VERSION_PATCH" in line:
                minfer_v = minfer_v + line[-2]
                break
            line = f.readline()
        f.close()

        pack_cmd += " --select_srlz "
        pack_cmd += " --minfer_v=%s" %minfer_v
        
    # select model token
    pack_cmd += " --token=%s " % (gcfg["token"])

    # select model compression
    if(gcfg["compress_model"]):
        pack_cmd += " --compress "

    # select model encryption
    if(gcfg["encrypt_model"]):
        pack_cmd += " --encrypt "

    # select output path
    proj_cfg["model_output_path"] = proj_cfg["proj_build_path"] + "/model_output"
    pack_cmd += " --output_path=%s " % (proj_cfg["model_output_path"])

    # select platform
    if(proj_cfg["arch"] == "aarch64"):
        pack_cmd += " --platform=%s " % ("armv8")
    elif(proj_cfg["arch"] == "armv7l"):
        pack_cmd += " --platform=%s " % ("armv7l")
    elif(proj_cfg["arch"] == "android-aarch64"):
        pack_cmd += " --platform=%s " % ("armv8")
    elif(proj_cfg["arch"] == "x86_64"):
        pack_cmd += " --platform=%s " % ("x86_64")
    else:
        print "non-supported arch: %s " % (proj_cfg["arch"])
        return

    ## process srlz model
    #if(gcfg["srlz_model"]):
    #    print "model process cmd: " + process_cmd
    #    proj_cfg["model process cmd"] = process_cmd
    #    os.system(process_cmd)

    print "model pack cmd: " + pack_cmd
    proj_cfg["model pack cmd"] = pack_cmd
    os.system(pack_cmd)

def upx_lib(path):
    cmd = "cd %s; mkdir lib_uncompressed; chmod +x lib/libmomenta_dms.so; mv lib/libmomenta_dms.so  lib_uncompressed/; upx lib_uncompressed/libmomenta_dms.so -v -o lib/libmomenta_dms.so; cd -" % (path)
    os.system(cmd)

def rel_pack(gcfg, proj_cfg):
    build_rel_path = proj_cfg["proj_release_path"] + ("/%s-%s-%s" %(proj_cfg["arch"], proj_cfg["os"], proj_cfg["cc"]))
    shutil.rmtree(build_rel_path, True)
    proj_cfg["build_rel_path"] = build_rel_path

    # pack lib
    if(os.path.exists(proj_cfg["proj_install_path"] + "/lib")):
        shutil.copytree(proj_cfg["proj_install_path"] + "/lib", build_rel_path + "/lib")
    if(gcfg["upx"] and proj_cfg["arch"] != "x86_64"):
        upx_lib("%s" % (build_rel_path))

    # pack minfer
    if(os.path.exists(proj_cfg["minfer_lib_dir"])):
        if("-static" not in proj_cfg["minfer"]): # using minfer-shared lib
            src_files = os.listdir(proj_cfg["minfer_lib_dir"])
            for file_name in src_files:
                full_file_name = os.path.join(proj_cfg["minfer_lib_dir"], file_name)
                if ".so" in full_file_name:
                    shutil.copy(full_file_name, build_rel_path + "/lib")

    # pack doc
    if(os.path.exists(proj_cfg["proj_install_path"] + "/doc")):
        shutil.copytree(proj_cfg["proj_install_path"] + "/doc/html", build_rel_path + "/doc/html")
        shutil.copy(proj_cfg["proj_install_path"] + "/doc/README.html", build_rel_path + "/doc")
        shutil.copy(proj_cfg["proj_install_path"] + "/doc/README.pdf", build_rel_path + "/doc")

    # pack test
    if(os.path.exists(proj_cfg["proj_install_path"] + "/test")):
        shutil.copytree(proj_cfg["proj_install_path"] + "/test", build_rel_path + "/test")

    # pack sample
    if(os.path.exists(proj_cfg["proj_install_path"] + "/samples")):
        shutil.copytree(proj_cfg["proj_install_path"] + "/samples", build_rel_path + "/samples")

    # pack model
    if("model_output_path" in proj_cfg and os.path.exists(proj_cfg["model_output_path"])):
        # export original model when needed
        if os.path.exists(proj_cfg["model_output_path"] + "/model.tar") and gcfg["export_origin_model"]:
            warning("EXPORTING ORIGINAL MODEL!")
            ensure_path(build_rel_path + "/data", False)
            shutil.copyfile(proj_cfg["model_output_path"] + "/model.tar", build_rel_path + "/data/origin_model.tar")

        for root, dirs, files in os.walk(proj_cfg["model_output_path"]):
            for dir in dirs:
                if dir == 'encrypt':
                        fullpath  =os.path.join(root, dir) + "/model.tar" # Get the full path to the file
                        ensure_path(build_rel_path + "/data", False)
                        shutil.copyfile(fullpath, build_rel_path + "/data/model.tar")
        
    # pack code
    if(os.path.exists(proj_cfg["proj_install_path"] + "/include")):
        shutil.copytree(proj_cfg["proj_install_path"] + "/include", build_rel_path + "/include")

def filter_header(text, features):
    private_features = features[:]
    private_features.append("debug")
    #private_features.append("private")

    htext = text
    ptext = text

    def filter_text(txt, list):
        # filter unused matches:
        pattern = "(\/\/\/.*@selector.*(\[.*\]).*\n)((?:.*|.*\n)*?)(\/\/\/.*@selector.*\n)"
        while True:
            m = re.search(pattern, txt)
            if not m:
                break
            f = eval(m.group(2))
            intersect = [i for i in f if i in list]

            if not intersect:
                txt = txt[:m.start()] + txt[m.end():]
            else:
                txt = txt[:m.start()] + txt[txt.find("\n", m.start()):]

        # remove anchor markers:
        pattern = "\/\/\/.*@selector.*\n"
        txt = re.sub(pattern, "", txt)
        return txt

    # common + private_selection = private
    # common + header_selection = header
    # nested condition is NOT supported for now
    htext = filter_text(htext, features)
    ptext = filter_text(ptext, private_features)

    return htext, ptext

def generate_proj_header(gcfg):
    for proj_cfg in gcfg["build_config"]["project"][gcfg["project"]]:
        if (not gcfg["no_header_gen"]):
            print "model_config_path: ", proj_cfg["model_config_path"]
            print "model_pool_path: ", proj_cfg["model_pool_path"]
            assert len(proj_cfg["model"]) != 0 and os.path.exists(proj_cfg["model_config_path"]) and os.path.exists(proj_cfg["model_pool_path"]), ("[error] invalid model name %s, cannot generate project header!!" % (proj_cfg["model"]))

            base_header = gcfg["root_path"] + "/adapter/src/momenta_dms_all.h"
            assert os.path.exists(base_header), "momenta_dms_all.h not exist!!!!"
            fin = open(base_header, "r").read()

            # filter header content for project:
            adapter_header_path = proj_cfg["adapter_root_path"] + "/include"
            ensure_path(adapter_header_path, True)
            fheader = open(adapter_header_path + "/momenta_dms.h", "w+")
            fprivate_header = open(adapter_header_path + "/momenta_dms_private.h", "w+")

            header, private = filter_header(fin, proj_cfg["feature"])

            fheader.write(header)
            fheader.close()

            fprivate_header.write(private)
            fprivate_header.close()

def generate_proj_version(gcfg):
    base_header = gcfg["root_path"] + "/adapter/src/momenta_dms_all.h"
    txt = open(base_header, "r").read()

    pattern_major = "(DMS_VERSION_MAJOR.*)(\d)"
    pattern_minor = "(DMS_VERSION_MINOR.*)(\d)"
    pattern_patch = "(DMS_VERSION_PATCH.*)(\d)"

    txt = re.sub(pattern_major, ("\g<1>%s" % (gcfg["version_major"])), txt)
    txt = re.sub(pattern_minor, ("\g<1>%s" % (gcfg["version_minor"])), txt)
    txt = re.sub(pattern_patch, ("\g<1>%s" % (gcfg["version_patch"])), txt)

    fout = open(base_header, "w")
    fout.write(txt)
    fout.close()
    
def build(cfg):
    # 1. parse args & config file
    assert os.path.exists(cfg["build_config"]), ("config file not exist @ %s" % (cfg["build_config"]))
    cfg["build_config"] = read_json(cfg["build_config"])

    if (cfg["release"]):
        print_msg_with_color("Starting a release build", "cyan")

        if not cfg["debug"]:
            cfg["strip"] = True
        else:
            warning("buidling debug mode for release! ONLY for debugging, not suitable for release!")
            warning("binary NOT STRIPPED!!!! because building debug mode!!!")

        cfg["doxygen"] = True
        cfg["encrypt_model"] = True
        cfg["compress_model"] = True

        if(cfg["no_srlz_model"]):
            warning("Using a NON-serilalized model!!")

        if(cfg["profile_time"]):
            warning("Profiling switched on for release-build, this will slow down the runtime!!")

        if(cfg["gcov"]):
            warning("Gcov switched on for release-build, this will slow down the runtime! And generate files!!")

        if(cfg["cppcheck"]):
            warning("Cppcheck switched on for release-build, this will slow down the runtime! And generate files!!")

    # 2. prepare build env
    root = get_root_path(".git")
    build_path = root + "/build"
    ensure_path(build_path)
    cfg["build_path"] = build_path
    cfg["root_path"] = root

    ver_pattern = "(\d).(\d).(\d)"
    m = re.search(ver_pattern, cfg["version"])
    cfg["version_major"] = m.group(1)
    cfg["version_minor"] = m.group(2)
    cfg["version_patch"] = m.group(3)

    assert cfg["project"] in cfg["build_config"]["project"], ("project %s not in config file " % (cfg["project"]))
    for proj in cfg["build_config"]["project"][cfg["project"]]:
        proj["model_config_path"] = cfg["root_path"]  + "/thirdparty/resource/dms-model-release/new_dms_models/project_configs/" +  proj["model"]
        proj["model_pool_path"]   = cfg["root_path"]  + "/thirdparty/resource/dms-model-release/new_dms_models/models"
        proj["adapter_root_path"] = cfg["root_path"] + "/adapter/" + cfg["project"]
        proj["model_config"] = read_json(proj["model_config_path"])

        if "feature" in proj["model_config"]:
            proj["feature"] = proj["model_config"]["feature"]

        if "build_cmd" in proj:
            for v, k in proj["build_cmd"].items():
                if (v not in cfg) or (cfg[v] != k):
                    warning(("Override build config [%s] to value [%s]. Original value: [%s]" % (v, k, cfg[v])))
                    cfg[v] = k

    # 3. generate project header
    generate_proj_version(cfg)
    generate_proj_header(cfg)

    # 4. build project binaries
    assert cfg["project"] in cfg["build_config"]["project"], ("project %s not in config file " % (cfg["project"]))
    for proj in cfg["build_config"]["project"][cfg["project"]]:
        build_env_set(cfg, proj)
        build_minfer_set(cfg, proj)
        build_cmake_set(cfg, proj)
        build_proj(cfg, proj)

        if(cfg["strip"]):
            strip_lib(cfg, proj)
            strip_test(cfg, proj)
            strip_sample(cfg, proj)

        # 5. build project model
        build_model(cfg, proj)

    # 6. build project doc
    if (cfg["doxygen"]):
        for proj in cfg["build_config"]["project"][cfg["project"]]:
                doxygen(cfg, proj)

    # 7. pack for release
    if(cfg["release"]):
        for proj in cfg["build_config"]["project"][cfg["project"]]:
            rel_pack(cfg, proj)

    # 8. prepare footprint for release
    if(cfg["release"]):
        for proj in cfg["build_config"]["project"][cfg["project"]]:
            # dump build config:
            lf = open(proj["proj_install_path"] + "/build_log.json", "w")
            lf.write(json.dumps(proj))
            lf.close()

            # prepare file md5 and git sha for release files:
            calculate_footprint(proj, cfg)

    # 9. print all warnings again at the end:
    print_all_warning()

    print "Project build done!"

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--project", choices=["s32v_demo", "sv51", "aptiv_fid", "aptiv_dms", "aptivgw_dms","saic_dms", "nxp", "ns_dms", "icc_v1", "desay_dms", "m56_dms_c1", "m56_dms_a2"], help="project to build")
    parser.add_argument("--build_config", default=".ci/build_config.json", help="build config for toolchain, project, etc...")
    parser.add_argument("--profile_time", action="store_true", default=False, help="Enable task profiling")
    parser.add_argument("--strip", action="store_true", default=False, help="whether strip code or not")
    parser.add_argument("--debug", action="store_true", default=False, help="Debug mode")
    parser.add_argument("--ib", action="store_true", default=False, help="incremental build switch")
    parser.add_argument("--build_test", action="store_true", default=False, help="Build test cases")
    parser.add_argument("--build_inspection", action="store_true", default=False, help="Enable task inspectation")
    parser.add_argument("--build_sample", action="store_true", default=False, help="Build samples")
    parser.add_argument("--no_header_gen", action="store_true", default=False, help="Build samples")
    parser.add_argument("--verbose", action="store_true", default=False, help="Verbose mode")
    parser.add_argument("--doxygen", action="store_true", default=False, help="documentation generation by doxygen")
    parser.add_argument("--release", action="store_true", default=False, help="documentation generation by doxygen")
    parser.add_argument("--encrypt_model", action="store_true", default=False, help="Encript model")
    parser.add_argument("--compress_model", action="store_true", default=False, help="Compress model using tar")
    parser.add_argument("--no_srlz_model", action="store_true", default=False, help="Select serialise model")
    parser.add_argument("--export_origin_model", action="store_true", default=False, help="Export original model when packing")
    parser.add_argument("--gcov", action="store_true", default=False, help="Enable gcov for inspecting code coverage")
    parser.add_argument("--cppcheck", action="store_true", default=False, help="Enable cppcheck for static analysis")
    parser.add_argument("--version", default=None, help="SDK_VERSION to define")
    parser.add_argument("--version_extra", default=None, help="extra version information to append")
    parser.add_argument("--token", default="XnKVlc5cDf2gP3Qb", help="SDK_TOKEN to match encrypt model")
    parser.add_argument("--upx", action="store_true", default=False, help="compress libs")

    args = parser.parse_args()

    build(vars(args))

    exit(0)
