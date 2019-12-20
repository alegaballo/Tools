#! /bin/bash
help_msg="Usage: $0 -b|--branches <branch_file> -t|--target <target_branch> -d|--direction (I/F) [--merge-options options]\n
        \t-d|--direction : I merge all branches in <branch_file> into <target_branch>\n\
        \t                 F merge <target_branch> into all branches in <branch_file>\n\
        \t-b|--branches <branch_file> : text file containing a list of branches, one per line\n\
        \t-t|--target <target_branch> : name of the target branch\n\
"

merge_branches() {
    branches=("$@")
    for branch in "${branches[@]}"; do
        cmd="git merge ${merge_options[@]} $branch"
        echo $cmd
        out=`$cmd`
        status=$?
        if [ $status -ne 0 ]; then
            echo $out
            exit 1
        fi
    done
    echo "DONE"
}

prepare_branch() {
    branch=$1
    cmd="git checkout $branch"
    echo "$cmd"
    out=`$cmd`
    status=$?
    if [ $status -ne 0 ]; then
        echo $out "return code: $status"
        exit 1
    else
        cmd="git pull"
        echo "$cmd"
        out=`$cmd`
        status=$?
        if [ $status -ne 0 ]; then
            echo $out $status
            exit 1
        else
            echo "ready to merge"
        fi
    fi
}

merge_from_branch() {
    source_branch=$1
    shift
    branches=("$@")
    for branch in ${branches[@]}; do
        prepare_branch $branch
        status=$?
        if [ $status -ne 0 ]; then
            echo "can't prepare $branch for merge with $source_branch"
            echo $out
            exit 1
        else
            cmd="git merge $source_branch ${merge_options[@]}"
            echo $cmd
            out=`$cmd`
            status=$?
            if [ $status -ne 0 ]; then
                echo "can't merge $1 in $branch"
                echo $out
                exit 1
            else
                cmd="git push"
                echo $cmd
                out=`$cmd`
                status=$?
                if [ $status -ne 0 ]; then
                    echo $out $status
                fi
            fi
        fi
    done
}

merge_I(){
    branch=$1
    shift
    branches=("$@")
    prepare_branch $branch
    merge_branches ${branches[@]}
}

merge_F(){
    branch=$1
    shift
    branches=("$@")
    merge_from_branch $branch ${branches[@]}
}


is_merge_option=0
declare -a merge_options
while [ "$1" != "" ]; do
    case $1 in
    -h | --help)
        echo -e "$help_msg"
        ;;
    -b | --branches)
        shift
        filename=$1
        is_merge_option=0
        ;;
    -t | --target)
        shift
        target_branch=$1
        is_merge_option=0
        ;;
    -d | --direction)
        shift
        direction=$1
        if [ $direction != "I" ] && [ $direction != "F" ]; then
            echo "invalid direction, only (I/F) allowed"
            exit 1
        fi
        ;;
    --merge_options)
        shift
        merge_options+=($1)
        is_merge_option=1
        ;;
    *) if [ $is_merge_option -gt 0 ]; then
        merge_options+=($1)
    else
        echo "invalid argument"
        exit
    fi ;;

    esac
    shift
done

if [ $filename ] && [ $target_branch ]  && [ $direction ]; then
    # merge_to_branch $target_branch
    # merge_from_branch $target_branch
    echo "good to go"
    # load branches into array
    declare -a branches
    mapfile -t branches <$filename
    # remove master and $target_branch from branches
    mapfile -d $' ' -t branches < <(echo -E "${branches[@]}" | sed -E "s/(^(master\s*|$target_branch\s*)|(\s*master|\s*$target_branch)$|(\s+master\s+|\s+$target_branch\s+))//gm")

    case $direction in
    "I")
        echo "I"
        merge_I $target_branch ${branches[@]}
        ;;
    "F")
        echo "F"
        merge_F $target_branch ${branches[@]}
        ;;
    esac
else
    echo -e "$help_msg"
fi
