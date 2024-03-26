import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from pathlib import Path
import xacro


PACKAGE_NAME = 'c_megarover_simulator'

def generate_launch_description():

    pkg_megarover_description = get_package_share_directory(
        'megarover_description')
    
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world_name = LaunchConfiguration('world_name', default='turtlebot3_world')
    
    launch_file_dir = os.path.join(get_package_share_directory(PACKAGE_NAME), 'launch')
    
    ign_resource_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',value=[
        os.path.join("/opt/ros/humble", "share"), ':' +
        #str(Path(pkg_megarover_description).parent.resolve()), ':' +
        os.path.join(get_package_share_directory(PACKAGE_NAME), "models")])
    
    # spawn robot. load xacro file from megarover_description package
    xacro_file = os.path.join(pkg_megarover_description,
                              'urdf',
                              'mega3.xacro')
    # xacroをロード
    doc = xacro.process_file(xacro_file, mappings={'use_sim' : use_sim_time})

    # xacroを展開してURDFを生成
    robot_desc = doc.toprettyxml(indent='  ')
    gz_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-string', robot_desc,
                   '-name', 'megarover',
                   '-allow_renaming', 'true',
                   '-x', '-2.0',
                   '-y', '-0.5',
                   '-z', '0.01'],
    )

    params = {'robot_description': robot_desc, 'use_sim_time': use_sim_time}
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )
    
    # Spawn world
    gz_spawn_world = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-file', PathJoinSubstitution([
                        get_package_share_directory(PACKAGE_NAME),
                        "models", "worlds", "model.sdf"]),
                     '-allow_renaming', 'false'],
    )
    

    world_only = os.path.join(get_package_share_directory(PACKAGE_NAME), "models", "worlds", "world_only.sdf")

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=[
                # Velocity command (ROS2 -> IGN)
                '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
                # Odometry (IGN -> ROS2)
                '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
                # TF (IGN -> ROS2)
                "/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V",
                # Clock (IGN -> ROS2)
                '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
                # Joint states (IGN -> ROS2)
                '/joint_states@sensor_msgs/msg/JointState[ignition.msgs.Model',

                #'/scan@sensor_msgs/msg/LaserScan@ignition.msgs.LaserScan',
                # /scan/points to PointCloud2
                '/scan/points@sensor_msgs/msg/PointCloud2@ignition.msgs.PointCloudPacked',
                # /imu to Imu
                '/imu@sensor_msgs/msg/Imu@ignition.msgs.IMU'
                ],
        remappings=[
                ('/scan/points', '/livox/lidar'),
                ('/imu', '/livox/imu'),
        ],
        output='screen'
    )


    return LaunchDescription([
        ign_resource_path,
        gz_spawn_world,
        gz_spawn_entity,
        bridge,
        node_robot_state_publisher,
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(get_package_share_directory('ros_ign_gazebo'),
                              'launch', 'ign_gazebo.launch.py')]),
            launch_arguments=[('ign_args', [' -r -v 3 ' +
                              world_only
                             ])]),
                             
        DeclareLaunchArgument(
            'use_sim_time',
            default_value=use_sim_time,
            description='If true, use simulated clock'),

        DeclareLaunchArgument(
            'world_name',
            default_value=world_name,
            description='World name'),

        #IncludeLaunchDescription(
        #    PythonLaunchDescriptionSource([launch_file_dir, '/ros_ign_bridge.launch.py']),
        #    launch_arguments={'use_sim_time': use_sim_time}.items(),
        #),

        #IncludeLaunchDescription(
        #    PythonLaunchDescriptionSource([launch_file_dir, '/robot_state_publisher.launch.py']),
        #    launch_arguments={'use_sim_time': use_sim_time}.items(),
        #),

        #IncludeLaunchDescription(
        #    PythonLaunchDescriptionSource([launch_file_dir, '/navigation2.launch.py']),
        #    launch_arguments={'use_sim_time': use_sim_time}.items(),
        #),
    ])